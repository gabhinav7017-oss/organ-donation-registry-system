from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from registry.models import Donor, Recipient, OrganMatch


class DashboardOrganStatusMapTest(TestCase):
    """Tests for the organ status map data used by the interactive body diagram."""

    def setUp(self):
        self.client = Client()

    def test_dashboard_returns_organ_status_map_in_context(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('organ_status_map', response.context)

    def test_organ_status_map_contains_all_organs(self):
        response = self.client.get(reverse('dashboard'))
        organ_status_map = response.context['organ_status_map']
        expected_organs = [
            'Kidney', 'Liver', 'Heart', 'Lungs', 'Pancreas',
            'Intestine', 'Corneas', 'Bone Marrow', 'Skin',
        ]
        for organ in expected_organs:
            self.assertIn(organ, organ_status_map)

    def test_organ_status_map_empty_database(self):
        response = self.client.get(reverse('dashboard'))
        organ_status_map = response.context['organ_status_map']
        for organ, info in organ_status_map.items():
            self.assertEqual(info['donors'], 0)
            self.assertEqual(info['recipients'], 0)
            self.assertEqual(info['state'], 'none')

    def test_organ_status_map_donor_only(self):
        Donor.objects.create(
            first_name='John', last_name='Doe',
            date_of_birth=date(1985, 3, 15),
            blood_type='O+', email='john@test.com',
            phone='555-0001', address='123 Main St',
            organs=['Heart', 'Kidney'], status='Active',
        )
        response = self.client.get(reverse('dashboard'))
        organ_status_map = response.context['organ_status_map']
        self.assertEqual(organ_status_map['Heart']['donors'], 1)
        self.assertEqual(organ_status_map['Heart']['recipients'], 0)
        self.assertEqual(organ_status_map['Heart']['state'], 'donor')
        self.assertEqual(organ_status_map['Kidney']['state'], 'donor')
        self.assertEqual(organ_status_map['Liver']['state'], 'none')

    def test_organ_status_map_recipient_only(self):
        Recipient.objects.create(
            first_name='Alice', last_name='Brown',
            date_of_birth=date(1992, 1, 10),
            blood_type='O+', email='alice@test.com',
            phone='555-0004', address='321 Elm St',
            organ_needed='Heart', urgency='Critical', status='Active',
        )
        response = self.client.get(reverse('dashboard'))
        organ_status_map = response.context['organ_status_map']
        self.assertEqual(organ_status_map['Heart']['donors'], 0)
        self.assertEqual(organ_status_map['Heart']['recipients'], 1)
        self.assertEqual(organ_status_map['Heart']['state'], 'recipient')

    def test_organ_status_map_both_donor_and_recipient(self):
        Donor.objects.create(
            first_name='John', last_name='Doe',
            date_of_birth=date(1985, 3, 15),
            blood_type='O+', email='john@test.com',
            phone='555-0001', address='123 Main St',
            organs=['Heart'], status='Active',
        )
        Recipient.objects.create(
            first_name='Alice', last_name='Brown',
            date_of_birth=date(1992, 1, 10),
            blood_type='O+', email='alice@test.com',
            phone='555-0004', address='321 Elm St',
            organ_needed='Heart', urgency='Critical', status='Active',
        )
        response = self.client.get(reverse('dashboard'))
        organ_status_map = response.context['organ_status_map']
        self.assertEqual(organ_status_map['Heart']['donors'], 1)
        self.assertEqual(organ_status_map['Heart']['recipients'], 1)
        self.assertEqual(organ_status_map['Heart']['state'], 'both')

    def test_inactive_donors_excluded_from_organ_counts(self):
        Donor.objects.create(
            first_name='John', last_name='Doe',
            date_of_birth=date(1985, 3, 15),
            blood_type='O+', email='john@test.com',
            phone='555-0001', address='123 Main St',
            organs=['Heart'], status='Inactive',
        )
        response = self.client.get(reverse('dashboard'))
        organ_status_map = response.context['organ_status_map']
        self.assertEqual(organ_status_map['Heart']['donors'], 0)
        self.assertEqual(organ_status_map['Heart']['state'], 'none')

    def test_inactive_recipients_excluded_from_organ_counts(self):
        Recipient.objects.create(
            first_name='Alice', last_name='Brown',
            date_of_birth=date(1992, 1, 10),
            blood_type='O+', email='alice@test.com',
            phone='555-0004', address='321 Elm St',
            organ_needed='Heart', urgency='Critical', status='Inactive',
        )
        response = self.client.get(reverse('dashboard'))
        organ_status_map = response.context['organ_status_map']
        self.assertEqual(organ_status_map['Heart']['recipients'], 0)
        self.assertEqual(organ_status_map['Heart']['state'], 'none')

    def test_dashboard_renders_human_body_svg(self):
        response = self.client.get(reverse('dashboard'))
        content = response.content.decode()
        self.assertIn('human-body-svg', content)
        self.assertIn('Interactive Organ Map', content)

    def test_dashboard_renders_organ_regions(self):
        response = self.client.get(reverse('dashboard'))
        content = response.content.decode()
        organs = ['Corneas', 'Heart', 'Lungs', 'Liver', 'Pancreas',
                  'Kidney', 'Intestine', 'Bone Marrow', 'Skin']
        for organ in organs:
            self.assertIn(f'data-organ="{organ}"', content)

    def test_dashboard_renders_legend(self):
        response = self.client.get(reverse('dashboard'))
        content = response.content.decode()
        self.assertIn('Donors &amp; Recipients', content)
        self.assertIn('Donors Only', content)
        self.assertIn('Recipients Only', content)
        self.assertIn('No Activity', content)

    def test_organ_status_map_json_script_tag(self):
        response = self.client.get(reverse('dashboard'))
        content = response.content.decode()
        self.assertIn('id="organ-status-map"', content)

    def test_multiple_donors_for_same_organ(self):
        Donor.objects.create(
            first_name='John', last_name='Doe',
            date_of_birth=date(1985, 3, 15),
            blood_type='O+', email='john@test.com',
            phone='555-0001', address='123 Main St',
            organs=['Kidney'], status='Active',
        )
        Donor.objects.create(
            first_name='Jane', last_name='Smith',
            date_of_birth=date(1990, 7, 22),
            blood_type='A+', email='jane@test.com',
            phone='555-0002', address='456 Oak Ave',
            organs=['Kidney', 'Liver'], status='Active',
        )
        response = self.client.get(reverse('dashboard'))
        organ_status_map = response.context['organ_status_map']
        self.assertEqual(organ_status_map['Kidney']['donors'], 2)
        self.assertEqual(organ_status_map['Liver']['donors'], 1)

