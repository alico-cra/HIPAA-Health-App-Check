# HIPAA-Health-App-Check
Unofficial examination tool for aiding tool developers on health security steps they should be taking. Based on the [FTC tool](https://www.ftc.gov/business-guidance/resources/mobile-health-apps-interactive-tool).

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/alico-cra/HIPAA-Health-App-Check/badge)](https://scorecard.dev/viewer/?uri=github.com/{alico-cra}/{HIPAA-Health-App-Check})

## Architecture

```
┌─────────────────────────────────────┐
│  Current Repository                 │
│                                     │
│  ├── .github/workflows/             │
│  │   └── compliance-check.yaml      │  ← Reusable workflow template
│  └── compliance_check.py            │  ← Python assessment tool (reference)
└─────────────────────────────────────┘
                  ↑
                  │ uses (reusable workflow)
                  │
┌─────────────────────────────────────┐
│  Tool Repository                    │
│  (your health tool/app)             │
│                                     │
│  ├── .github/workflows/             │
│  │   └── compliance.yaml            │  ← Calls reusable workflow
│  └── src/                           │
│      └── (your app code)            │
└─────────────────────────────────────┘
```

## Step 1: Set Up Your Tool Repository

### 1.1 Create and Configure Survey Answers
1. Create a new `compliance-config.json` file at the root level of your tool repository
2. Add a single object and answer each question below based on YOUR tool:

* Question 1 (collects_health_info): Does/will your tool collect, share, use, or maintain health information?
* Question 2 (has_identifiable_health_info): Does the information fall within HIPAA's definition of "individually identifiable health information"?
* Question 3a (is_health_plan): Are you a health plan?
* Question 3b (is_healthcare_provider): Are you a health care provider (doctor, dentist, psychologist, hospital, clinic, pharmacy)?
* Question 4a (offers_certified_hit): Do you develop, offer, or sell any certified health information technology?
* Question 4b (enables_ehi_exchange): Do you enable electronic health information exchange among more than two unaffiliated parties?
* Question 5 (requires_prescription): Do consumers need a prescription to access your tool?
* Question 6 (works_for_covered_entity): Are you developing, offering, or operating a tool on behalf of a HIPAA covered entity?
Or are you a subcontractor to another entity providing services to a covered entity?
* Question 7 (intended_for_medical_use): Is your tool intended for:
    - use in the diagnosis of disease or other conditions?
    - use in the cure, mitigation, treatment, or prevention of disease?
    - to affect the structure or any function of the body?
* Question 8 (is_administrative_or_lifestyle_only): Is your tool solely intended for:
    - administrative support of a health care facility?
    - maintaining or encouraging a healthy lifestyle?
    - serving as electronic patient records?
    - transferring, storing, converting formats, or displaying data?
    - providing limited clinical decision support to a health care provider?
* Question 9 (is_low_risk): Does your tool pose a "low risk" to patients? (helps patients self-manage without specific treatment suggestions, or automates simple tasks)
* Question 10 (has_fda_regulated_function): Does your tool include a device software function that is the focus of FDA's oversight?
* Question 11 (is_consumer_facing): Is your tool for use by consumers?
* Question 12 (interacts_with_phr): Does your tool:
    - collect, receive, or maintain identifiable health information for consumers?
    - access health information in personal health records?
    - send health information to personal health records?
    - offer products/services through a website that maintains health records?
    - provide services to an entity that maintains health records?
* Question 13 (intended_for_children): Is your tool intended for children?
* Question 14 (has_child_oriented_features): Does your tool use child-oriented activities, incentives, design, music, etc.?
* Question 15 (children_using_app): Do you have actual knowledge that children are using your tool?
* Question 16 (offers_substance_use_treatment): Does your tool offer substance use disorder treatment service or product?

```json
{
    "collects_health_info": true,
    "has_identifiable_health_info": true,
    "is_health_plan": false,
    "is_healthcare_provider": false,
    "offers_certified_hit": false,
    "enables_ehi_exchange": false,
    "requires_prescription": false,
    "works_for_covered_entity": false,
    "intended_for_medical_use": false,
    "is_administrative_or_lifestyle_only": true,
    "is_low_risk": true,
    "has_fda_regulated_function": false,
    "is_consumer_facing": true,
    "interacts_with_phr": true,
    "intended_for_children": false,
    "has_child_oriented_features": false,
    "children_using_app": false,
    "offers_substance_use_treatment": false
}
```

### 1.2 Add Consumer Workflow
* Create `.github/workflows/compliance.yaml` in your tool repository
* Copy this snippet over to your `compliance.yaml` file:

```yaml
name: CI - Health App Compliance

on:
    push:
        branches: [main]
    pull_request:
        branches: [main]

jobs:
    # Extract Python version from your project (optional)
    extract-python-version:
        runs-on: ubuntu-latest
        outputs:
            python-version: ${{ steps.get-version.outputs.python-version }}
        steps:
            - name: Checkout repository
              uses: actions/checkout@v4

            - name: Get Python version
              id: get-version
              run: |
                  # Try to extract from pyproject.toml, .python-version, or default to 3.13
                  if [ -f "pyproject.toml" ]; then
                    VERSION=$(grep -oP 'requires-python = ">=\K[0-9.]+' pyproject.toml | head -1 || echo "3.13")
                  elif [ -f ".python-version" ]; then
                    VERSION=$(cat .python-version)
                  else
                    VERSION="3.13"
                  fi
                  echo "python-version=$VERSION" >> $GITHUB_OUTPUT
                  echo "Detected Python version: $VERSION"

    # Run the compliance assessment using the reusable workflow
    compliance-assessment:
        needs: extract-python-version
        uses: alico-cra/HIPAA-Health-App-Check/.github/workflows/compliance-check.yaml@main
        with:
            python-version: ${{ needs.extract-python-version.outputs.python-version }}
            fail-on-warnings: true
            upload-report: true
```

## Understanding the Output

### Exit Codes
- **0**: No critical warnings detected
- **1**: Critical warnings detected (see report)

### Outputs Available
- `has-warnings`: boolean - Whether critical warnings exist
- `applicable-laws`: number - Count of applicable laws/regulations

### Artifacts Generated
- `compliance-assessment-report/`
  - `compliance_output.txt` - Full text report

## Workflow Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `python-version` | string | `3.13` | Python version to use |
| `compliance-config-path` | string | `main.py` | Path to compliance script |
| `fail-on-warnings` | boolean | `true` | Fail workflow on critical warnings |
| `upload-report` | boolean | `true` | Upload compliance report artifact |

## Example: Using Custom Parameters

```yaml
compliance-assessment:
  uses: alico-cra/HIPAA-Health-App-Check/.github/workflows/compliance-check.yaml@main
  with:
    python-version: '3.13'
    compliance-config-path: 'tools/compliance/check.py'
    fail-on-warnings: false  # Warning only, don't fail CI
    upload-report: true
```


## Troubleshooting

### Workflow Not Found
**Error**: `Error: alico-cra/HIPAA-Health-App-Check/.github/workflows/compliance-check.yaml@main not found`

**Solution**: 
- Verify template repository name is correct
- Ensure workflow file exists at exact path
- Check repository is public or you have access
- Verify branch name (`main` vs `master`)

### Permission Denied
**Error**: Issues/PRs can't be created

**Solution**:
- Go to repository **Settings → Actions → General**
- Under "Workflow permissions", select "Read and write permissions"
- Enable "Allow GitHub Actions to create and approve pull requests"

## Best Practices

### 1. Review Configuration Regularly
As your app evolves, update `compliance-config.json` accordingly:
- Adding new features? Re-answer the questions
- Changing data collection? Update configuration
- New integrations? Reassess compliance needs

### 2. Don't Ignore Warnings
Warnings indicate potential compliance gaps:
- ⚠️ **FDA Regulated**: May need pre-market approval
- ⚠️ **Breach Notification**: Legal requirement with penalties
- ⚠️ **Children's Data**: COPPA has strict requirements

### 3. Consult Legal Counsel
This tool provides guidance, not legal advice:
- Use it as a starting point for compliance discussions
- Share reports with your legal team
- Get professional review

### 4. Schedule Regular Checks
The workflow runs weekly by default:
- Review compliance reports monthly
- Update configuration when features change
- Re-run after major releases

## Resources

### Federal Agencies
- [FTC Mobile Health Apps Tool](https://www.ftc.gov/business-guidance/resources/mobile-health-apps-interactive-tool)
- [HHS HIPAA Resources](https://www.hhs.gov/hipaa/index.html)
- [FDA Digital Health Center](https://www.fda.gov/medical-devices/digital-health-center-excellence)
- [HealthIT.gov Information Blocking](https://www.healthit.gov/topic/information-blocking)

### Compliance Guides
- [FTC Best Practices for Mobile Health Apps](https://www.ftc.gov/tips-advice/business-center/guidance/mobile-health-app-developers-ftc-best-practices)
- [HIPAA for Mobile Apps](https://www.hhs.gov/hipaa/for-professionals/special-topics/health-apps/index.html)
- [COPPA Compliance](https://www.ftc.gov/business-guidance/privacy-security/childrens-privacy)

## License & Disclaimer

This tool is provided for informational purposes only and does not constitute legal advice. Use of this tool does not guarantee compliance with applicable federal requirements. Always consult with qualified legal counsel to ensure full compliance with all applicable laws and regulations.

The software version of this tool is offered under the Apache-2.0 license.

## Citation
- See [CITATION.cff](./CITATION.cff)

---

**Questions?** Open an issue or contact Charles River Analytics, a GRVTY Company for further details.