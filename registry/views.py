from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
import hashlib
from .models import Donor, Recipient, OrganMatch, BLOOD_COMPATIBILITY, BLOOD_TYPE_CHOICES, ORGAN_CHOICES, MATCH_STATUS_CHOICES
from .forms import DonorForm, RecipientForm, OrganMatchForm


# ──────────────────────────────────────────────
#  Dashboard
# ──────────────────────────────────────────────

def dashboard(request):
    def hashed_coordinate(seed_text, min_lat=28.35, max_lat=28.90, min_lng=76.85, max_lng=77.45):
        digest = hashlib.sha256(seed_text.encode('utf-8')).hexdigest()
        lat_ratio = int(digest[:8], 16) / 0xFFFFFFFF
        lng_ratio = int(digest[8:16], 16) / 0xFFFFFFFF
        latitude = min_lat + (max_lat - min_lat) * lat_ratio
        longitude = min_lng + (max_lng - min_lng) * lng_ratio
        return round(latitude, 5), round(longitude, 5)

    total_donors = Donor.objects.count()
    active_donors = Donor.objects.filter(status='Active').count()
    total_recipients = Recipient.objects.count()
    active_recipients = Recipient.objects.filter(status='Active').count()
    total_matches = OrganMatch.objects.count()
    pending_matches = OrganMatch.objects.filter(status='Pending').count()
    completed_matches = OrganMatch.objects.filter(status='Completed').count()
    recent_donors = Donor.objects.all()[:5]
    recent_recipients = Recipient.objects.all()[:5]
    recent_matches = OrganMatch.objects.select_related('donor', 'recipient').all()[:5]

    urgency_stats = {
        'Critical': Recipient.objects.filter(urgency='Critical', status='Active').count(),
        'High': Recipient.objects.filter(urgency='High', status='Active').count(),
        'Medium': Recipient.objects.filter(urgency='Medium', status='Active').count(),
        'Low': Recipient.objects.filter(urgency='Low', status='Active').count(),
    }

    donor_blood_counts = list(
        Donor.objects.values('blood_type')
        .annotate(total=Count('id'))
        .order_by('blood_type')
    )

    organ_available_counts = list(
        Donor.objects.filter(status='Active')
        .values('organs')
    )
    organ_totals = {label: 0 for _, label in ORGAN_CHOICES}
    for donor_organs in organ_available_counts:
        for organ in donor_organs.get('organs', []):
            if organ in organ_totals:
                organ_totals[organ] += 1

    recipient_organ_counts = {
        item['organ_needed']: item['total']
        for item in Recipient.objects.filter(status='Active')
        .values('organ_needed')
        .annotate(total=Count('id'))
    }

    organ_status_map = {}
    for organ_name, donor_count in organ_totals.items():
        recipient_count = recipient_organ_counts.get(organ_name, 0)
        if donor_count > 0 and recipient_count > 0:
            state = 'both'
        elif donor_count > 0:
            state = 'donor'
        elif recipient_count > 0:
            state = 'recipient'
        else:
            state = 'none'
        organ_status_map[organ_name] = {
            'donors': donor_count,
            'recipients': recipient_count,
            'state': state,
        }

    organ_status_ui = {
        'heart': organ_status_map.get('Heart', {'donors': 0, 'recipients': 0, 'state': 'none'}),
        'lungs': organ_status_map.get('Lungs', {'donors': 0, 'recipients': 0, 'state': 'none'}),
        'liver': organ_status_map.get('Liver', {'donors': 0, 'recipients': 0, 'state': 'none'}),
        'kidney': organ_status_map.get('Kidney', {'donors': 0, 'recipients': 0, 'state': 'none'}),
        'pancreas': organ_status_map.get('Pancreas', {'donors': 0, 'recipients': 0, 'state': 'none'}),
        'intestine': organ_status_map.get('Intestine', {'donors': 0, 'recipients': 0, 'state': 'none'}),
        'corneas': organ_status_map.get('Corneas', {'donors': 0, 'recipients': 0, 'state': 'none'}),
        'skin': organ_status_map.get('Skin', {'donors': 0, 'recipients': 0, 'state': 'none'}),
        'bone_marrow': organ_status_map.get('Bone Marrow', {'donors': 0, 'recipients': 0, 'state': 'none'}),
    }

    organ_display_order = [
        ('heart', 'Heart'),
        ('lungs', 'Lungs'),
        ('liver', 'Liver'),
        ('kidney', 'Kidney'),
        ('pancreas', 'Pancreas'),
        ('intestine', 'Intestine'),
        ('corneas', 'Corneas'),
        ('bone_marrow', 'Bone Marrow'),
        ('skin', 'Skin'),
    ]

    organ_regions = []
    for key, label in organ_display_order:
        organ_info = organ_status_ui[key]
        organ_regions.append({
            'key': key,
            'label': label,
            'donors': organ_info['donors'],
            'recipients': organ_info['recipients'],
            'state': organ_info['state'],
        })

    organ_chart_labels = [item['label'] for item in organ_regions]
    organ_chart_donors = [item['donors'] for item in organ_regions]
    organ_chart_recipients = [item['recipients'] for item in organ_regions]

    donors_for_map = list(Donor.objects.filter(status='Active').order_by('-registered_at')[:22])
    recipients_for_map = list(Recipient.objects.filter(status='Active').order_by('-registered_at')[:22])

    donor_locations = []
    donor_point_index = {}
    for donor in donors_for_map:
        latitude, longitude = hashed_coordinate(f"donor-{donor.pk}-{donor.address}-{donor.email}")
        donor_payload = {
            'id': donor.pk,
            'name': donor.full_name,
            'blood_type': donor.blood_type,
            'organs': donor.organs,
            'phone': donor.phone,
            'lat': latitude,
            'lng': longitude,
        }
        donor_locations.append(donor_payload)
        donor_point_index[donor.pk] = donor_payload

    recipient_locations = []
    recipient_point_index = {}
    for recipient in recipients_for_map:
        latitude, longitude = hashed_coordinate(f"recipient-{recipient.pk}-{recipient.address}-{recipient.email}")
        recipient_payload = {
            'id': recipient.pk,
            'name': recipient.full_name,
            'blood_type': recipient.blood_type,
            'organ_needed': recipient.organ_needed,
            'urgency': recipient.urgency,
            'phone': recipient.phone,
            'lat': latitude,
            'lng': longitude,
            'urgent': recipient.urgency in ['Critical', 'High'],
        }
        recipient_locations.append(recipient_payload)
        recipient_point_index[recipient.pk] = recipient_payload

    matched_links = []
    link_candidates = OrganMatch.objects.select_related('donor', 'recipient').order_by('-matched_at')[:20]
    for match in link_candidates:
        donor_point = donor_point_index.get(match.donor_id)
        recipient_point = recipient_point_index.get(match.recipient_id)
        if donor_point and recipient_point:
            matched_links.append({
                'from': [donor_point['lat'], donor_point['lng']],
                'to': [recipient_point['lat'], recipient_point['lng']],
                'organ': match.organ,
                'status': match.status,
            })

    top_organs = sorted(organ_totals.items(), key=lambda item: item[1], reverse=True)
    available_organ_names = [name for name, total in top_organs if total > 0][:4]
    if not available_organ_names:
        available_organ_names = ['Kidney', 'Liver', 'Corneas']

    hospital_locations = [
        {
            'name': 'Apollo Transplant Centre',
            'lat': 28.5672,
            'lng': 77.2100,
            'contact': '+91-11-2682-5050',
            'organs': available_organ_names,
        },
        {
            'name': 'AIIMS Organ Retrieval Unit',
            'lat': 28.5678,
            'lng': 77.2107,
            'contact': '+91-11-2658-8500',
            'organs': available_organ_names[:3],
        },
        {
            'name': 'Fortis Transplant Hub',
            'lat': 28.4595,
            'lng': 77.0266,
            'contact': '+91-124-492-1021',
            'organs': available_organ_names,
        },
        {
            'name': 'Max Super Speciality',
            'lat': 28.6328,
            'lng': 77.2183,
            'contact': '+91-11-4055-4055',
            'organs': available_organ_names[:2],
        },
        {
            'name': 'City Command Hospital',
            'lat': 28.6139,
            'lng': 77.2090,
            'contact': '+91-11-2200-9000',
            'organs': available_organ_names,
        },
    ]

    recipient_urgency_counts = list(
        Recipient.objects.filter(status='Active')
        .values('urgency')
        .annotate(total=Count('id'))
        .order_by('urgency')
    )

    context = {
        'total_donors': total_donors,
        'active_donors': active_donors,
        'total_recipients': total_recipients,
        'active_recipients': active_recipients,
        'total_matches': total_matches,
        'pending_matches': pending_matches,
        'completed_matches': completed_matches,
        'recent_donors': recent_donors,
        'recent_recipients': recent_recipients,
        'recent_matches': recent_matches,
        'urgency_stats': urgency_stats,
        'donor_blood_labels': [item['blood_type'] for item in donor_blood_counts],
        'donor_blood_values': [item['total'] for item in donor_blood_counts],
        'recipient_urgency_labels': [item['urgency'] for item in recipient_urgency_counts],
        'recipient_urgency_values': [item['total'] for item in recipient_urgency_counts],
        'organ_status_map': organ_status_map,
        'organ_status_ui': organ_status_ui,
        'organ_regions': organ_regions,
        'organ_chart_labels': organ_chart_labels,
        'organ_chart_donors': organ_chart_donors,
        'organ_chart_recipients': organ_chart_recipients,
        'hospital_locations': hospital_locations,
        'donor_locations': donor_locations,
        'recipient_locations': recipient_locations,
        'matched_links': matched_links,
        'urgent_requests_count': sum(1 for item in recipient_locations if item['urgent']),
        'nearby_hospitals': hospital_locations[:4],
    }
    return render(request, 'registry/dashboard.html', context)


# ──────────────────────────────────────────────
#  Donor Views
# ──────────────────────────────────────────────

def donor_list(request):
    query = request.GET.get('q', '')
    blood_type = request.GET.get('blood_type', '')
    status = request.GET.get('status', '')
    donors = Donor.objects.all()
    if query:
        donors = donors.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
        )
    if blood_type:
        donors = donors.filter(blood_type=blood_type)
    if status:
        donors = donors.filter(status=status)
    return render(request, 'registry/donor_list.html', {
        'donors': donors,
        'query': query,
        'blood_type': blood_type,
        'status': status,
        'blood_type_choices': BLOOD_TYPE_CHOICES,
    })


def donor_detail(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    matches = OrganMatch.objects.filter(donor=donor).select_related('recipient')
    return render(request, 'registry/donor_detail.html', {'donor': donor, 'matches': matches})


def donor_create(request):
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donor registered successfully.')
            return redirect('donor_list')
    else:
        form = DonorForm()
    return render(request, 'registry/donor_form.html', {'form': form, 'title': 'Register Donor'})


def donor_edit(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    if request.method == 'POST':
        form = DonorForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donor updated successfully.')
            return redirect('donor_detail', pk=pk)
    else:
        form = DonorForm(instance=donor)
    return render(request, 'registry/donor_form.html', {'form': form, 'title': 'Edit Donor', 'donor': donor})


def donor_delete(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    if request.method == 'POST':
        donor.delete()
        messages.success(request, 'Donor record deleted.')
        return redirect('donor_list')
    return render(request, 'registry/confirm_delete.html', {'object': donor, 'type': 'Donor'})


# ──────────────────────────────────────────────
#  Recipient Views
# ──────────────────────────────────────────────

def recipient_list(request):
    query = request.GET.get('q', '')
    blood_type = request.GET.get('blood_type', '')
    organ = request.GET.get('organ', '')
    urgency = request.GET.get('urgency', '')
    recipients = Recipient.objects.all()
    if query:
        recipients = recipients.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
        )
    if blood_type:
        recipients = recipients.filter(blood_type=blood_type)
    if organ:
        recipients = recipients.filter(organ_needed=organ)
    if urgency:
        recipients = recipients.filter(urgency=urgency)
    return render(request, 'registry/recipient_list.html', {
        'recipients': recipients,
        'query': query,
        'blood_type': blood_type,
        'organ': organ,
        'urgency': urgency,
        'blood_type_choices': BLOOD_TYPE_CHOICES,
        'organ_choices': ORGAN_CHOICES,
    })


def recipient_detail(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    matches = OrganMatch.objects.filter(recipient=recipient).select_related('donor')
    return render(request, 'registry/recipient_detail.html', {'recipient': recipient, 'matches': matches})


def recipient_create(request):
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recipient registered successfully.')
            return redirect('recipient_list')
    else:
        form = RecipientForm()
    return render(request, 'registry/recipient_form.html', {'form': form, 'title': 'Register Recipient'})


def recipient_edit(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recipient updated successfully.')
            return redirect('recipient_detail', pk=pk)
    else:
        form = RecipientForm(instance=recipient)
    return render(request, 'registry/recipient_form.html', {
        'form': form, 'title': 'Edit Recipient', 'recipient': recipient,
    })


def recipient_delete(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        recipient.delete()
        messages.success(request, 'Recipient record deleted.')
        return redirect('recipient_list')
    return render(request, 'registry/confirm_delete.html', {'object': recipient, 'type': 'Recipient'})


# ──────────────────────────────────────────────
#  Organ Matching Views
# ──────────────────────────────────────────────

def match_list(request):
    status_filter = request.GET.get('status', '')
    matches = OrganMatch.objects.select_related('donor', 'recipient').all()
    if status_filter:
        matches = matches.filter(status=status_filter)
    return render(request, 'registry/match_list.html', {
        'matches': matches,
        'status_filter': status_filter,
        'status_choices': MATCH_STATUS_CHOICES,
    })


def match_detail(request, pk):
    match = get_object_or_404(OrganMatch.objects.select_related('donor', 'recipient'), pk=pk)
    return render(request, 'registry/match_detail.html', {'match': match})


def match_create(request):
    if request.method == 'POST':
        form = OrganMatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match recorded successfully.')
            return redirect('match_list')
    else:
        form = OrganMatchForm()
    return render(request, 'registry/match_form.html', {'form': form, 'title': 'Create Match'})


def match_edit(request, pk):
    match = get_object_or_404(OrganMatch, pk=pk)
    if request.method == 'POST':
        form = OrganMatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match updated.')
            return redirect('match_detail', pk=pk)
    else:
        form = OrganMatchForm(instance=match)
    return render(request, 'registry/match_form.html', {'form': form, 'title': 'Edit Match', 'match': match})


def match_delete(request, pk):
    match = get_object_or_404(OrganMatch, pk=pk)
    if request.method == 'POST':
        match.delete()
        messages.success(request, 'Match deleted.')
        return redirect('match_list')
    return render(request, 'registry/confirm_delete.html', {'object': match, 'type': 'Match'})


def auto_match(request):
    """Auto-match active recipients with compatible active donors."""
    recipients = Recipient.objects.filter(status='Active')
    suggestions = []
    for recipient in recipients:
        compatible_blood_types = [
            donor_type for donor_type, compatible in BLOOD_COMPATIBILITY.items()
            if recipient.blood_type in compatible
        ]
        compatible_donors = Donor.objects.filter(
            status='Active',
            blood_type__in=compatible_blood_types,
        )
        for donor in compatible_donors:
            if recipient.organ_needed in donor.organs:
                already_matched = OrganMatch.objects.filter(
                    donor=donor,
                    recipient=recipient,
                    organ=recipient.organ_needed,
                ).exists()
                if not already_matched:
                    suggestions.append({
                        'donor': donor,
                        'recipient': recipient,
                        'organ': recipient.organ_needed,
                    })

    if request.method == 'POST':
        donor_id = request.POST.get('donor_id')
        recipient_id = request.POST.get('recipient_id')
        organ = request.POST.get('organ')
        if donor_id and recipient_id and organ:
            donor = get_object_or_404(Donor, pk=donor_id)
            recipient = get_object_or_404(Recipient, pk=recipient_id)
            match, created = OrganMatch.objects.get_or_create(
                donor=donor, recipient=recipient, organ=organ,
                defaults={'status': 'Pending'},
            )
            if created:
                messages.success(request, f'Match created: {organ} — {donor.full_name} → {recipient.full_name}')
            else:
                messages.info(request, 'This match already exists.')
        return redirect('auto_match')

    return render(request, 'registry/auto_match.html', {'suggestions': suggestions})
