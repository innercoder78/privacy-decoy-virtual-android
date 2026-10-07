# Source and provenance policy

Every proposed runtime, VMM, hypervisor helper, guest component, native dependency,
build tool and reused source requires review before adoption. References are not
dependencies and upstream demonstrations are not PDVA security evidence.

The adoption record must provide exact upstream identity and immutable revision;
license and file-level provenance where code is inherited; source completeness;
dependency graph and transitive/native/binary inventory; reproducible build and
artifact correspondence; security history and unresolved issues; TCB role and
authority; update/maintenance owner; distribution/invocation rights and an explicit
reviewed adoption decision. Record rejected, unknown and excluded components.

A permissive root license does not establish licensing or source completeness for
every bundled file. No opaque security-critical binary may enter the TCB simply
because it makes a demo work. Do not import engine code, images, proprietary
packages, native libraries or predecessor scaffolding during the bootstrap.

CI/build dependencies require the same clear identity and risk accounting,
proportionate to their role. The only bootstrap external action is the reviewed
official checkout pin in the [catalog](source-reference-catalog.md). Standard-library
Python adds no package dependency. Hosted runner software is execution infrastructure,
not a reproducibly pinned Android toolchain or product dependency.

Keep the catalog organized by technical role. Cataloging is not adoption; any
future candidate needs its own review, not a license inferred from a project name.
Maintain public-repository hygiene for all logs/artifacts and do not publish
private paths, credentials or confidential source while investigating provenance.
