from crispy_forms.layout import Layout, Div, HTML

from django import forms
from crispy_forms.helper import FormHelper

CAMPAIGN_STATUSES = (
    ('Pending', 'PENDING'),
    ('Running', 'RUNNING'),
    ('Finished', 'FINISHED'),
    ('Failed', 'FAILED')
)

PROPOSAL_STATUSES = (
    ('Pending', 'PENDING'),
    ('Approved', 'APPROVED'),
    ('Rejected', 'REJECTED'),
    ('Finished', 'FINISHED'),
)

PROPOSAL_TYPE = (
    ('Charity', 'CHARITY'),
    ('Sports', 'SPORTS'),
    ('Technology', 'TECHNOLOGY'),
    ('Art', 'ART'),
    ('Animals', 'ANIMALS'),
    ('Culture', 'CULTURE'),
    ('Community projects', 'COMMUNITY_PROJECTS'),
)

documentation_html = """
        <div id="documentation">
            <div id="documentation_title">
                Campaign documentation:
            </div>
            <div id="documentation_files">
            {% for key, value in data.campaignProposalDocumentIds.items %}
                {% if not forloop.last %}
                    <div class="filename">
                        <a href="https://ct-campaign-service.herokuapp.com/campaignProposal/{{ data.id }}/doc/{{ key }}">{{ value }}</a>,&nbsp;
                    </div>
                {% elif forloop.last %}
                    <div class="filename">
                        <a href="https://ct-campaign-service.herokuapp.com/campaignProposal/{{ data.id }}/doc/{{ key }}">{{ value }}</a>
                    </div>
                {% endif %}
            {% endfor %}
            </div>
        </div>
"""


class EditCampaignForm(forms.Form):
    helper = FormHelper()
    helper.form_tag = False
    helper.layout = Layout(Div(
        Div('campaign_type', css_class='col-sm-6',),
        Div('project_location', css_class='col-sm-6',),
        Div('permanent_residence', css_class='col-sm-6',),
        Div('email', css_class='col-sm-6',),
        Div('mobile_number', css_class='col-sm-6',),
        Div('IBAN', css_class='col-sm-6',),
        Div('campaign_page_url', css_class='col-sm-6',),
        Div('description', css_class='col-sm-6',),
        Div('comments', css_class='col-sm-6',),
        Div('status', css_class='col-sm-12',),
    ),
)

    campaign_type = forms.CharField(max_length=100, disabled=True)
    permanent_residence = forms.CharField(max_length=100, disabled=True)
    email = forms.EmailField(max_length=100, disabled=True)
    mobile_number = forms.CharField(max_length=100, disabled=True)
    IBAN = forms.CharField(max_length=100, disabled=True)
    campaign_page_url = forms.CharField(max_length=100, disabled=True)
    description = forms.CharField(widget=forms.Textarea, disabled=True)
    comments = forms.CharField(widget=forms.Textarea, label="Approver Comments")
    status = forms.ChoiceField(label='Status', choices=CAMPAIGN_STATUSES, disabled=True)


class EditProposalForm(forms.Form):
    helper = FormHelper()
    helper.form_tag = False
    helper.layout = Layout(Div(
        Div('campaign_type', css_class='col-sm-6',),
        Div('project_location', css_class='col-sm-6',),
        Div('permanent_residence', css_class='col-sm-6',),
        Div('email', css_class='col-sm-6',),
        Div('mobile_number', css_class='col-sm-6',),
        Div('IBAN', css_class='col-sm-6',),
        Div('campaign_page_url', css_class='col-sm-6',),
        Div('campaign_page_id', css_class='col-sm-6',),
        Div('description', css_class='col-sm-6',),
        Div('comments', css_class='col-sm-6',),
        HTML(documentation_html),
        Div('status', css_class='col-sm-12',),
    ),
)

    campaign_type = forms.ChoiceField(label='Type', choices=PROPOSAL_TYPE)
    permanent_residence = forms.CharField(max_length=100, disabled=True)
    email = forms.EmailField(max_length=100, disabled=True)
    mobile_number = forms.CharField(max_length=100, disabled=True)
    project_location = forms.CharField(max_length=100, disabled=True)
    IBAN = forms.CharField(max_length=100, disabled=True)
    campaign_page_url = forms.CharField(max_length=100)
    campaign_page_id = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    comments = forms.CharField(widget=forms.Textarea, label="Approver Comments")
    status = forms.ChoiceField(label='Status', choices=PROPOSAL_STATUSES)


class EditProposalFormApproved(EditProposalForm):
    def __init__(self, *args, **kwargs):
        super(EditProposalForm, self).__init__(*args, **kwargs)

    status = forms.ChoiceField(label='Status', choices=PROPOSAL_STATUSES, disabled=True)


class UnpledgeForm(forms.Form):
    pledge_id = forms.CharField(max_length=100, disabled=True)