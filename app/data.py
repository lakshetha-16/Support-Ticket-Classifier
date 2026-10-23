"""Synthetic support-ticket examples for a self-contained student project."""
import random

TEMPLATES = {
    "Billing": {
        "high": [
            "I was charged twice for my subscription and need the duplicate payment reversed today.",
            "A large unexpected charge appeared on my invoice and my account is at risk of suspension.",
            "Our business account was billed incorrectly for several users and payment is due today.",
        ],
        "medium": [
            "My monthly invoice has the wrong amount and I would like someone to review it.",
            "I cancelled my plan but the latest invoice still includes the subscription fee.",
            "The discount is missing from my bill. Can you check the invoice?",
        ],
        "low": [
            "Where can I download a receipt for last month's payment?",
            "Could you explain the difference between the monthly and annual plan prices?",
            "I need a copy of an older invoice for my records.",
        ],
    },
    "Technical Issue": {
        "high": [
            "The application is down for our whole team and we cannot access customer records.",
            "Every login attempt returns a server error and our staff cannot work.",
            "The production service keeps crashing for all users after the latest update.",
        ],
        "medium": [
            "The dashboard freezes whenever I open the reports page.",
            "File uploads fail intermittently even though my internet connection is stable.",
            "The app is very slow when loading large projects this afternoon.",
        ],
        "low": [
            "The date format looks different on the settings page.",
            "A chart takes a few seconds longer than expected to load.",
            "I noticed a small alignment issue in the activity panel.",
        ],
    },
    "Account Access": {
        "high": [
            "I am locked out of the administrator account and payroll processing starts soon.",
            "Our team cannot sign in and the password reset emails never arrive.",
            "The account recovery process fails for all users in our organisation.",
        ],
        "medium": [
            "I changed my phone and can no longer complete two factor authentication.",
            "My password reset link says it has expired even though I just received it.",
            "I can sign in on my laptop but not on the mobile app.",
        ],
        "low": [
            "How do I update the email address on my profile?",
            "Where can I change my profile picture and display name?",
            "Can I add a second email address to my account?",
        ],
    },
    "Feature Request": {
        "high": [
            "We need bulk export before our compliance review tomorrow or our team will be blocked.",
            "Please add an urgent approval workflow because the current process blocks today's release.",
            "Our users cannot complete the required workflow without a priority integration.",
        ],
        "medium": [
            "Could you add a CSV export option to the reports page?",
            "It would help if projects could be sorted by last updated date.",
            "Please consider adding dark mode to the dashboard.",
        ],
        "low": [
            "A keyboard shortcut for opening search would be a nice improvement.",
            "Could the profile page support a custom avatar?",
            "It would be useful to rename saved report views.",
        ],
    },
    "Security": {
        "high": [
            "I see unknown administrator logins and suspect our account has been compromised.",
            "Customer data may have been exposed through a public link. Please investigate immediately.",
            "An unauthorised person changed our security settings and we cannot revoke their access.",
        ],
        "medium": [
            "I received a suspicious password reset email that I did not request.",
            "A former employee still appears in our team access list.",
            "The audit log does not show who changed a user's permissions.",
        ],
        "low": [
            "Where can I review the active sessions on my account?",
            "Can you explain how to enable security notifications?",
            "I would like guidance on rotating my API token as a precaution.",
        ],
    },
    "Service Outage": {
        "high": [
            "The service is unavailable across our region and our operations are completely blocked.",
            "All requests are timing out and customers cannot use the platform at all.",
            "A major outage has stopped our entire department from processing orders.",
        ],
        "medium": [
            "The service has been intermittently unavailable for several minutes.",
            "Some users receive gateway errors when opening the workspace.",
            "The API response times are elevated and requests occasionally time out.",
        ],
        "low": [
            "Is there a planned maintenance window this weekend?",
            "The status page updated slowly during the maintenance period.",
            "Could you share where service availability announcements are posted?",
        ],
    },
}

PREFIXES = [
    "Hello support, ", "Hi team, ", "Please help: ", "I need assistance because ",
    "Could you investigate? ", "Good morning, ", ""
]
SUFFIXES = [
    " This is affecting my work.", " Please let me know the next steps.",
    " Thank you for checking.", " I have tried again and the issue remains.",
    " Please update me when you can.", ""
]

def build_dataset(seed: int = 21):
    """Create reproducible synthetic text examples; not real customer data."""
    rng = random.Random(seed)
    rows = []
    for category, priorities in TEMPLATES.items():
        for priority, examples in priorities.items():
            for example in examples:
                for _ in range(10):
                    text = f"{rng.choice(PREFIXES)}{example}{rng.choice(SUFFIXES)}"
                    rows.append({"text": text, "category": category, "priority": priority})
    # Add a little realistic wording variation without changing labels.
    rng.shuffle(rows)
    return rows
