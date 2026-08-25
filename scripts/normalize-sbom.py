#!/usr/bin/env python3
"""Normalise a Trivy SPDX document into a stable, committable artifact.

Trivy's raw output is not reproducible: the document namespace carries a fresh
UUID, and every timestamp is "now". Committed as-is, each scheduled run would
rewrite all SBOMs and produce a commit even when no dependency changed. This
script pins the volatile fields to the scanned commit and records provenance in
the document itself, so an unchanged dependency tree yields a byte-identical file.

IMPORTANT: the scan must be run from inside the checkout as `trivy fs ... .`.
Trivy derives every package SPDXID from a PkgID that includes the scan path, so
scanning `src` instead of `.` changes every identifier in the document and makes
the whole file churn. See .github/workflows/refresh-sbom.yml.

Usage:
    normalize-sbom.py --input raw.spdx.json --output assets/sbom/<slug>.spdx.json \
                      --slug <slug> --repo <repo> --source <checkout-dir>
"""

import argparse
import json
import os
import subprocess

NAMESPACE_BASE = "https://public-service-as-a-service.github.io/api-catalogue/sbom"


def git(source, *args):
    # TZ=UTC so `format-local` really is UTC -- the timestamps are written with a
    # trailing Z and SPDX requires them to be UTC.
    return subprocess.run(
        ["git", "-C", source, *args],
        capture_output=True, text=True, check=True, env={**os.environ, "TZ": "UTC"},
    ).stdout.strip()


def commit_info(source):
    """Return (full sha, short sha, commit date as SPDX UTC timestamp)."""
    sha = git(source, "rev-parse", "HEAD")
    date = git(source, "log", "-1", "--date=format-local:%Y-%m-%dT%H:%M:%SZ", "--format=%cd")
    return sha, sha[:7], date


def trivy_version(doc):
    for creator in doc.get("creationInfo", {}).get("creators", []):
        if creator.startswith("Tool: trivy-"):
            return creator[len("Tool: "):]
    return "trivy"


def package_key(pkg):
    return (pkg.get("name", ""), pkg.get("versionInfo", ""), pkg.get("SPDXID", ""))


def relationship_key(rel):
    return (
        rel.get("spdxElementId", ""),
        rel.get("relationshipType", ""),
        rel.get("relatedSpdxElement", ""),
    )


def normalise(doc, slug, repo, sha, short_sha, date):
    """Pin volatile fields to the scanned commit and sort for readable diffs."""
    doc["name"] = f"{repo}@{short_sha}"
    doc["documentNamespace"] = f"{NAMESPACE_BASE}/{slug}/{sha}"

    creation = doc.setdefault("creationInfo", {})
    creation["created"] = date
    creation["comment"] = (
        f"Genererad ur {repo} commit {sha} ({date}) med {trivy_version(doc)}. "
        "Underhålls av .github/workflows/refresh-sbom.yml i api-catalogue."
    )

    # Trivy stamps every package with the scan root ("git+."), which is not a valid
    # SPDX download location and would also leak the scan path into the document.
    # The repository packages get the real clone URL; for third-party components we
    # do not assert one -- the purl in externalRefs already identifies them.
    repo_url = f"git+https://github.com/Sundsvallskommun/{repo}.git"
    for pkg in doc.get("packages", []):
        # Trivy's annotations are tool-internal (PkgID, PkgType, Class, SchemaVersion)
        # and carry no meaning for an SBOM consumer -- the purl in externalRefs is the
        # identifier. Dropping them removes ~30% of the file and, since each one is
        # stamped with the scan time, the last source of run-to-run volatility.
        pkg.pop("annotations", None)
        if pkg.get("downloadLocation", "").startswith("git+"):
            pkg["downloadLocation"] = repo_url if not pkg.get("externalRefs") else "NOASSERTION"
        # The scanned root is named "." after the scan path; give it the repo name.
        # SPDXID is left alone -- relationships reference it.
        if pkg.get("name") == ".":
            pkg["name"] = repo

    doc["packages"] = sorted(doc.get("packages", []), key=package_key)
    doc["relationships"] = sorted(doc.get("relationships", []), key=relationship_key)
    doc["hasExtractedLicensingInfos"] = sorted(
        doc.get("hasExtractedLicensingInfos", []), key=lambda x: x.get("licenseId", "")
    )
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="raw Trivy SPDX JSON")
    parser.add_argument("--output", required=True, help="normalised SPDX JSON to write")
    parser.add_argument("--slug", required=True, help="catalogue slug")
    parser.add_argument("--repo", required=True, help="source repository name")
    parser.add_argument("--source", required=True, help="path to the scanned checkout")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        doc = json.load(f)

    sha, short_sha, date = commit_info(args.source)
    doc = normalise(doc, args.slug, args.repo, sha, short_sha, date)

    components = sum(1 for p in doc.get("packages", []) if p.get("externalRefs"))
    if components < 50:
        print(f"WARNING: {args.slug} has only {components} components - "
              "Trivy may have failed to resolve the pom")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(f"{args.slug}: {components} components, commit {short_sha}")


if __name__ == "__main__":
    main()
