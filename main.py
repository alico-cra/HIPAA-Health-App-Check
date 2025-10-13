#!/usr/bin/env python3
"""
Mobile Health App Compliance Assessment Tool
Based on FTC's Mobile Health Apps Interactive Tool

This tool helps identify which federal laws and regulations may apply to your health app.
Configure your answers in the compliance_config dictionary below.
"""

import argparse
import json
import sys
from typing import Dict, List, Set
from dataclasses import dataclass, field


@dataclass
class ComplianceResult:
    """Results of the compliance assessment"""

    applicable_laws: Set[str] = field(default_factory=set)
    recommendations: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    resources: Dict[str, str] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


# CONFIGURE YOUR APP DETAILS HERE
# compliance_config = {
#     # Question 1: Does/will your app collect, share, use, or maintain health information?
#     "collects_health_info": True,
#     # Question 2: Does the information fall within HIPAA's definition of "individually identifiable health information"?
#     "has_identifiable_health_info": True,
#     # Question 3a: Are you a health plan?
#     "is_health_plan": False,
#     # Question 3b: Are you a health care provider (doctor, dentist, psychologist, hospital, clinic, pharmacy)?
#     "is_healthcare_provider": False,
#     # Question 4a: Do you develop, offer, or sell any certified health information technology?
#     "offers_certified_hit": False,
#     # Question 4b: Do you enable electronic health information exchange among more than two unaffiliated parties?
#     "enables_ehi_exchange": False,
#     # Question 5: Do consumers need a prescription to access your app?
#     "requires_prescription": False,
#     # Question 6: Are you developing, offering, or operating an app on behalf of a HIPAA covered entity?
#     # Or are you a subcontractor to another entity providing services to a covered entity?
#     "works_for_covered_entity": False,
#     # Question 7: Is your app intended for:
#     # - use in the diagnosis of disease or other conditions?
#     # - use in the cure, mitigation, treatment, or prevention of disease?
#     # - to affect the structure or any function of the body?
#     "intended_for_medical_use": False,
#     # Question 8: Is your app solely intended for:
#     # - administrative support of a health care facility?
#     # - maintaining or encouraging a healthy lifestyle?
#     # - serving as electronic patient records?
#     # - transferring, storing, converting formats, or displaying data?
#     # - providing limited clinical decision support to a health care provider?
#     "is_administrative_or_lifestyle_only": True,
#     # Question 9: Does your app pose a "low risk" to patients?
#     # (helps patients self-manage without specific treatment suggestions, or automates simple tasks)
#     "is_low_risk": True,
#     # Question 10: Does your app include a device software function that is the focus of FDA's oversight?
#     "has_fda_regulated_function": False,
#     # Question 11: Is your app for use by consumers?
#     "is_consumer_facing": True,
#     # Question 12: Does your app:
#     # - collect, receive, or maintain identifiable health information for consumers?
#     # - access health information in personal health records?
#     # - send health information to personal health records?
#     # - offer products/services through a website that maintains health records?
#     # - provide services to an entity that maintains health records?
#     "interacts_with_phr": True,
#     # Question 13: Is your app intended for children?
#     "intended_for_children": False,
#     # Question 14: Does your app use child-oriented activities, incentives, design, music, etc.?
#     "has_child_oriented_features": False,
#     # Question 15: Do you have actual knowledge that children are using your app?
#     "children_using_app": False,
#     # Question 16: Does your app offer substance use disorder treatment service or product?
#     "offers_substance_use_treatment": False,
# }


class HealthAppComplianceChecker:
    """Evaluates health app compliance with federal regulations"""

    def __init__(self, config: Dict):
        self.config = config
        self.result = ComplianceResult()

    def evaluate(self) -> ComplianceResult:
        """Run all compliance checks and return results"""

        # Check if health information is collected
        if not self.config["collects_health_info"]:
            self.result.recommendations.append(
                "Your app may not be subject to health-specific regulations if it doesn't "
                "collect health information, but general consumer protection laws may still apply."
            )
            return self.result

        # Check HIPAA applicability
        self._check_hipaa()

        # Check FDA applicability
        self._check_fda()

        # Check Information Blocking regulations
        self._check_information_blocking()

        # Check FTC Act (applies to most apps)
        self._check_ftc_act()

        # Check FTC Health Breach Notification Rule
        self._check_health_breach_notification()

        # Check COPPA
        self._check_coppa()

        # Check OARFPA
        self._check_oarfpa()

        # Add general recommendations
        self._add_general_recommendations()

        return self.result

    def _check_hipaa(self):
        """Check if HIPAA Rules apply"""
        is_covered_entity = (
            self.config["is_health_plan"] or self.config["is_healthcare_provider"]
        )

        is_business_associate = self.config["works_for_covered_entity"]

        if is_covered_entity or is_business_associate:
            self.result.applicable_laws.add("HIPAA Rules")

            if is_covered_entity:
                self.result.required_actions.append(
                    "As a HIPAA covered entity, you must comply with HIPAA Privacy, Security, "
                    "and Breach Notification Rules for all Protected Health Information (PHI)."
                )
            else:
                self.result.required_actions.append(
                    "As a HIPAA business associate, you must sign a Business Associate Agreement (BAA) "
                    "and comply with HIPAA Privacy, Security, and Breach Notification Rules."
                )

            self.result.resources["HIPAA"] = "https://www.hhs.gov/hipaa/index.html"
            self.result.resources["HIPAA for Mobile Apps"] = (
                "https://www.hhs.gov/hipaa/for-professionals/special-topics/health-apps/index.html"
            )
        else:
            if self.config["has_identifiable_health_info"]:
                self.result.recommendations.append(
                    "HIPAA does not apply to your app, but other federal laws (like the FTC Act) "
                    "still require you to protect consumer health information with reasonable "
                    "privacy and security practices."
                )

    def _check_fda(self):
        """Check if FDA regulations apply"""
        if self.config["intended_for_medical_use"]:
            # Check for exemptions
            if self.config["is_administrative_or_lifestyle_only"]:
                self.result.recommendations.append(
                    "Your app may be exempt from FDA device regulation under Section 520(o) "
                    "of the 21st Century Cures Act if it's solely for administrative support "
                    "or healthy lifestyle maintenance."
                )
                return

            if (
                self.config["is_low_risk"]
                and not self.config["has_fda_regulated_function"]
            ):
                self.result.recommendations.append(
                    "Your app may be considered low-risk by the FDA. FDA does not intend to "
                    "enforce device requirements for low-risk apps that help patients self-manage "
                    "or automate simple tasks."
                )
            elif self.config["has_fda_regulated_function"]:
                self.result.applicable_laws.add(
                    "Federal Food, Drug, and Cosmetic Act (FD&C Act)"
                )
                self.result.required_actions.append(
                    "Your app contains a device software function that is the focus of FDA's "
                    "regulatory oversight. You must comply with FDA medical device regulations."
                )
                self.result.warnings.append(
                    "FDA REGULATED DEVICE: Your app may require pre-market review, registration, "
                    "and ongoing compliance. Contact FDA immediately."
                )
                self.result.resources["FDA Digital Health"] = (
                    "https://www.fda.gov/medical-devices/digital-health-center-excellence"
                )
                self.result.resources["FDA Policy Navigator"] = (
                    "https://www.fda.gov/medical-devices/digital-health-center-excellence/"
                    "digital-health-policy-navigator"
                )
            elif self.config["requires_prescription"]:
                self.result.applicable_laws.add(
                    "Federal Food, Drug, and Cosmetic Act (FD&C Act)"
                )
                self.result.required_actions.append(
                    "Apps requiring a prescription are likely subject to FDA regulation as "
                    "medical devices."
                )

    def _check_information_blocking(self):
        """Check if Information Blocking regulations apply"""
        if (
            self.config["is_healthcare_provider"]
            or self.config["offers_certified_hit"]
            or self.config["enables_ehi_exchange"]
        ):

            self.result.applicable_laws.add(
                "21st Century Cures Act - Information Blocking Regulations"
            )

            actor_type = []
            if self.config["is_healthcare_provider"]:
                actor_type.append("health care provider")
            if self.config["offers_certified_hit"]:
                actor_type.append("health IT developer of certified health IT")
            if self.config["enables_ehi_exchange"]:
                actor_type.append("health information network/exchange")

            self.result.required_actions.append(
                f"As a {', '.join(actor_type)}, you must comply with Information Blocking "
                "regulations. You cannot engage in practices that interfere with access, "
                "exchange, or use of Electronic Health Information (EHI) unless covered by "
                "a regulatory exception."
            )

            if self.config["offers_certified_hit"]:
                self.result.required_actions.append(
                    "If you certify health IT through the ASTP/ONC Health IT Certification Program, "
                    "your technology must meet specific privacy and security requirements and you "
                    "must make certain public attestations."
                )

            self.result.resources["Information Blocking"] = (
                "https://www.healthit.gov/topic/information-blocking"
            )

    def _check_ftc_act(self):
        """Check FTC Act applicability"""
        self.result.applicable_laws.add("Federal Trade Commission Act (FTC Act)")

        self.result.required_actions.append(
            "Section 5 of the FTC Act applies to most app developers. You must:"
        )
        self.result.required_actions.append(
            "  • Have reasonable privacy and security practices"
        )
        self.result.required_actions.append(
            "  • Honor your privacy policy and any promises made to users"
        )
        self.result.required_actions.append(
            "  • Not engage in unfair or deceptive practices regarding data collection, use, or security"
        )

        if self.config["offers_certified_hit"]:
            self.result.required_actions.append(
                "  • Live up to any transparency attestations made through the ONC Health IT Certification Program"
            )

        self.result.resources["FTC Privacy & Security"] = (
            "https://www.ftc.gov/business-guidance/privacy-security"
        )

    def _check_health_breach_notification(self):
        """Check FTC Health Breach Notification Rule"""
        if (
            self.config["is_consumer_facing"]
            and self.config["interacts_with_phr"]
            and not (
                self.config["is_health_plan"]
                or self.config["is_healthcare_provider"]
                or self.config["works_for_covered_entity"]
            )
        ):

            self.result.applicable_laws.add("FTC Health Breach Notification Rule")

            self.result.required_actions.append(
                "You must provide breach notifications to consumers, the FTC, and in some cases "
                "the media, following any unauthorized access to or acquisition of unsecured "
                "identifiable health information."
            )

            self.result.warnings.append(
                "BREACH NOTIFICATION REQUIRED: Failure to provide required breach notifications "
                "can result in significant civil penalties from the FTC."
            )

            self.result.resources["Health Breach Notification Rule"] = (
                "https://www.ftc.gov/legal-library/browse/rules/health-breach-notification-rule"
            )

    def _check_coppa(self):
        """Check COPPA applicability"""
        if (
            self.config["intended_for_children"]
            or self.config["has_child_oriented_features"]
            or self.config["children_using_app"]
        ):

            self.result.applicable_laws.add(
                "Children's Online Privacy Protection Act (COPPA)"
            )

            self.result.required_actions.append("COPPA requires you to:")
            self.result.required_actions.append(
                "  • Provide clear notice to parents about what information you collect from children under 13"
            )
            self.result.required_actions.append(
                "  • Obtain verifiable parental consent before collecting children's personal information"
            )
            self.result.required_actions.append(
                "  • Establish reasonable procedures to protect children's information"
            )

            self.result.warnings.append(
                "CHILDREN'S DATA: Apps collecting data from children under 13 have strict requirements. "
                "Consult with legal counsel familiar with COPPA."
            )

            self.result.resources["COPPA"] = (
                "https://www.ftc.gov/business-guidance/privacy-security/childrens-privacy"
            )

    def _check_oarfpa(self):
        """Check OARFPA applicability"""
        if self.config["offers_substance_use_treatment"]:
            self.result.applicable_laws.add(
                "Opioid Addiction Recovery Fraud Prevention Act (OARFPA)"
            )

            self.result.required_actions.append(
                "The FTC can seek civil penalties for unfair or deceptive acts or practices "
                "related to substance use disorder treatment services or products."
            )

            self.result.warnings.append(
                "SUBSTANCE USE TREATMENT: Enhanced scrutiny applies. Ensure all claims about "
                "treatment efficacy are truthful and not misleading."
            )

    def _add_general_recommendations(self):
        """Add general best practices recommendations"""
        self.result.recommendations.append(
            "Implement reasonable data security measures including encryption, access controls, "
            "and regular security assessments."
        )
        self.result.recommendations.append(
            "Create a clear, prominent privacy policy that explains what data you collect, "
            "how you use it, who you share it with, and how users can access or delete their data."
        )
        self.result.recommendations.append(
            "Obtain meaningful consent from users before collecting or sharing their health information."
        )
        self.result.recommendations.append(
            "Minimize data collection to only what's necessary for your app's functionality."
        )
        self.result.recommendations.append(
            "Implement data retention and deletion policies."
        )

        self.result.resources["FTC Best Practices for Mobile Health Apps"] = (
            "https://www.ftc.gov/tips-advice/business-center/guidance/mobile-health-app-developers-ftc-best-practices"
        )

    def print_report(self):
        """Print a formatted compliance report"""
        result = self.evaluate()

        print("\n" + "=" * 80)
        print("MOBILE HEALTH APP COMPLIANCE ASSESSMENT REPORT")
        print("=" * 80 + "\n")

        # Warnings
        if result.warnings:
            print("⚠️  CRITICAL WARNINGS:")
            print("-" * 80)
            for warning in result.warnings:
                print(f"  ⚠️  {warning}\n")

        # Applicable Laws
        print("📋 APPLICABLE FEDERAL LAWS & REGULATIONS:")
        print("-" * 80)
        if result.applicable_laws:
            for law in sorted(result.applicable_laws):
                print(f"  ✓ {law}")
        else:
            print("  No specific health regulations identified, but general consumer")
            print("  protection laws may still apply.")
        print()

        # Required Actions
        if result.required_actions:
            print("✅ REQUIRED COMPLIANCE ACTIONS:")
            print("-" * 80)
            for action in result.required_actions:
                if action.startswith("  •"):
                    print(action)
                else:
                    print(f"  • {action}")
            print()

        # Recommendations
        if result.recommendations:
            print("💡 RECOMMENDATIONS & BEST PRACTICES:")
            print("-" * 80)
            for rec in result.recommendations:
                print(f"  • {rec}")
            print()

        # Resources
        print("📚 HELPFUL RESOURCES:")
        print("-" * 80)
        for name, url in result.resources.items():
            print(f"  • {name}")
            print(f"    {url}")
        print()

        print("=" * 80)
        print("DISCLAIMER: This tool provides informational guidance only and does not")
        print("constitute legal advice. Consult with qualified legal counsel to ensure")
        print("full compliance with all applicable laws and regulations.")
        print("=" * 80 + "\n")

        # Exit with error code if there are warnings
        return 1 if result.warnings else 0


def main():
    """Main entry point"""
    print("\n🏥 Mobile Health App Compliance Assessment Tool")
    print("Based on FTC's Mobile Health Apps Interactive Tool\n")

    # Get the path to the JSON file from the first command-line argument
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="Path to the JSON file")
    args = parser.parse_args()

    with open(args.json_file, "r", encoding="utf-8") as f:
        answer_dict = json.load(f)

        checker = HealthAppComplianceChecker(config=answer_dict)
        exit_code = checker.print_report()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
