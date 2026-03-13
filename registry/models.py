from django.db import models
from django.utils import timezone


BLOOD_TYPE_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]

ORGAN_CHOICES = [
    ('Kidney', 'Kidney'),
    ('Liver', 'Liver'),
    ('Heart', 'Heart'),
    ('Lungs', 'Lungs'),
    ('Pancreas', 'Pancreas'),
    ('Intestine', 'Intestine'),
    ('Corneas', 'Corneas'),
    ('Bone Marrow', 'Bone Marrow'),
    ('Skin', 'Skin'),
]

URGENCY_CHOICES = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
    ('Critical', 'Critical'),
]

STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Matched', 'Matched'),
    ('Inactive', 'Inactive'),
]

MATCH_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Completed', 'Completed'),
    ('Rejected', 'Rejected'),
]

# Blood type compatibility: donor blood type -> list of compatible recipient blood types
BLOOD_COMPATIBILITY = {
    'O-':  ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+':  ['O+', 'A+', 'B+', 'AB+'],
    'A-':  ['A-', 'A+', 'AB-', 'AB+'],
    'A+':  ['A+', 'AB+'],
    'B-':  ['B-', 'B+', 'AB-', 'AB+'],
    'B+':  ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],
}


class Donor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    organs = models.JSONField(default=list, help_text="List of organs willing to donate")
    medical_notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    registered_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.blood_type})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-registered_at']


class Recipient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    organ_needed = models.CharField(max_length=20, choices=ORGAN_CHOICES)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='Medium')
    medical_notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    registered_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (needs {self.organ_needed})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-registered_at']


class OrganMatch(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='matches')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='matches')
    organ = models.CharField(max_length=20, choices=ORGAN_CHOICES)
    status = models.CharField(max_length=10, choices=MATCH_STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True)
    matched_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organ}: {self.donor} → {self.recipient} [{self.status}]"

    class Meta:
        ordering = ['-matched_at']
        unique_together = [['donor', 'recipient', 'organ']]
