## Minimum viable knowledge sources

Use the raw source files rather than rendered HTML to avoid navigation and template noise.

### E3SM fundamentals

1. **E3SM configurations, compsets, grids, and input data**
   [https://raw.githubusercontent.com/E3SM-Project/E3SM/master/docs/user-guide/index.md](https://raw.githubusercontent.com/E3SM-Project/E3SM/master/docs/user-guide/index.md)

2. **Preparing an E3SM production simulation**
   [https://raw.githubusercontent.com/E3SM-Project/E3SM-Project.github.io/main/docs/running-e3sm-guide/guide-prior-to-production.md](https://raw.githubusercontent.com/E3SM-Project/E3SM-Project.github.io/main/docs/running-e3sm-guide/guide-prior-to-production.md)

3. **Running an E3SM production simulation**
   [https://raw.githubusercontent.com/E3SM-Project/E3SM-Project.github.io/main/docs/running-e3sm-guide/guide-production.md](https://raw.githubusercontent.com/E3SM-Project/E3SM-Project.github.io/main/docs/running-e3sm-guide/guide-production.md)

These establish the E3SM concepts and recommended simulation workflow. ([E3SM Project][1])

### CIME case workflow

4. **Discover machines, compsets, components, and grids**
   [https://raw.githubusercontent.com/ESMCI/cime/master/doc/source/ccs/query-configuration.rst](https://raw.githubusercontent.com/ESMCI/cime/master/doc/source/ccs/query-configuration.rst)

5. **Create and configure a case**
   [https://raw.githubusercontent.com/ESMCI/cime/master/doc/source/ccs/creating-a-case.rst](https://raw.githubusercontent.com/ESMCI/cime/master/doc/source/ccs/creating-a-case.rst)

6. **Run, continue, and resubmit a case**
   [https://raw.githubusercontent.com/ESMCI/cime/master/doc/source/ccs/running-a-case.rst](https://raw.githubusercontent.com/ESMCI/cime/master/doc/source/ccs/running-a-case.rst)

7. **Troubleshoot case failures**
   [https://raw.githubusercontent.com/ESMCI/cime/master/doc/source/ccs/troubleshooting.rst](https://raw.githubusercontent.com/ESMCI/cime/master/doc/source/ccs/troubleshooting.rst)

These cover the primary operational questions users will ask about CIME-managed E3SM simulations. ([GitHub][2])

### SimBoard context

8. **SimBoard purpose and capabilities**
   [https://raw.githubusercontent.com/E3SM-Project/simboard/main/README.md](https://raw.githubusercontent.com/E3SM-Project/simboard/main/README.md)

9. **SimBoard architecture and data flow**
   [https://raw.githubusercontent.com/E3SM-Project/simboard/main/docs/developer/README.md](https://raw.githubusercontent.com/E3SM-Project/simboard/main/docs/developer/README.md)

These let you test questions that combine general E3SM knowledge with SimBoard-specific behavior. ([GitHub][3])

Start with these **nine documents only**. Do not crawl linked pages initially. Store `repository`, `path`, `commit_sha`, `document_type`, and `source_url` as metadata, and record the resolved commit SHA because `main` and `master` are mutable.

[1]: https://docs.e3sm.org/E3SM/user-guide/ "User Guide - E3SM"
[2]: https://github.com/ESMCI/cime/blob/master/doc/source/ccs/query-configuration.rst "cime/doc/source/ccs/query-configuration.rst at master · ESMCI/cime · GitHub"
[3]: https://github.com/E3SM-Project/simboard "GitHub - E3SM-Project/simboard: SimBoard: The Next-Generation E3SM Web Interface for Simulation Metadata, Provenance, and Evaluation · GitHub"
