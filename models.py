from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models
from django.db.models import F, Q


# ============================================================
# Countries / geography
# ============================================================

class Country(models.Model):
    country_id = models.CharField(primary_key=True, max_length=2)
    name_country = models.CharField(max_length=100, blank=True, null=True)
    country_nationality = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "ci_countries"
        managed = True

    def __str__(self):
        return self.name_country or self.country_id


class State(models.Model):
    state_id = models.AutoField(primary_key=True)
    country = models.ForeignKey(
        "Country",
        on_delete=models.PROTECT,
        db_column="country_id",
        related_name="states",
    )
    state_name = models.CharField(max_length=100)

    class Meta:
        db_table = "ci_states"
        managed = True
        constraints = [
            models.UniqueConstraint(
                fields=["country", "state_name"],
                name="ci_states_country_name_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["country"], name="idx_ci_states_country_id"),
        ]

    def __str__(self):
        return self.state_name


class Locality(models.Model):
    locality_id = models.AutoField(primary_key=True)
    locality_state = models.ForeignKey(
        "State",
        on_delete=models.PROTECT,
        db_column="locality_state_id",
        related_name="localities",
    )
    locality_name = models.CharField(max_length=100)

    class Meta:
        db_table = "ci_localities"
        managed = True
        constraints = [
            models.UniqueConstraint(
                fields=["locality_state", "locality_name"],
                name="ci_localities_state_name_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["locality_state"], name="idx_ci_localities_state_id"),
        ]

    def __str__(self):
        return self.locality_name


# ============================================================
# Forums
# ============================================================

class Forum(models.Model):
    class ForumType(models.TextChoices):
        SUPERIOR_COURT = "Superior Court", "Superior Court"
        SUBORDINATE_COURT = "Subordinate Court", "Subordinate Court"
        TRIBUNAL = "Tribunal", "Tribunal"
        ARBITRAL_TRIBUNAL = "Arbitral Tribunal", "Arbitral Tribunal"
        ARBITRATION_CENTRE = "Arbitration Centre", "Arbitration Centre"
        OTHER = "Other", "Other"

    forum_id = models.AutoField(primary_key=True)
    forum_name = models.CharField(max_length=255)
    forum_type = models.CharField(max_length=50, choices=ForumType.choices)
    forum_station = models.CharField(max_length=100, blank=True, null=True)
    forum_address = models.CharField(max_length=100, blank=True, null=True)
    forum_locality = models.ForeignKey(
        "Locality",
        on_delete=models.PROTECT,
        db_column="forum_locality_id",
        blank=True,
        null=True,
        related_name="forums",
    )
    forum_zip = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = "ci_forums"
        managed = True
        constraints = [
            models.UniqueConstraint(
                fields=["forum_name", "forum_station", "forum_locality"],
                name="ci_forums_name_station_locality_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["forum_locality"], name="idx_ci_forums_locality_id"),
        ]

    def __str__(self):
        return self.forum_name


# ============================================================
# Legal entities and advocates
# ============================================================

class LegalEntity(models.Model):
    class EntityType(models.TextChoices):
        PRIVATE_LAW_FIRM = "Private Law Firm", "Private Law Firm"
        SOLE_PRACTITIONER = "Sole Practitioner", "Sole Practitioner"
        STATE_PROSECUTOR = "State Prosecutor (ODPP)", "State Prosecutor (ODPP)"
        ATTORNEY_GENERAL = "Attorney-General", "Attorney-General"
        OTHER_GOVERNMENT_LEGAL_OFFICE = "Other Government Legal Office", "Other Government Legal Office"
        OTHER = "Other", "Other"

    legalentity_id = models.AutoField(primary_key=True)
    entity_type = models.CharField(max_length=50, choices=EntityType.choices)
    entity_name = models.CharField(max_length=255)
    entity_address = models.CharField(max_length=100, blank=True, null=True)
    entity_locality = models.ForeignKey(
        "Locality",
        on_delete=models.PROTECT,
        db_column="entity_locality",
        blank=True,
        null=True,
        related_name="legal_entities",
    )

    class Meta:
        db_table = "ci_legalentities"
        managed = True

    def __str__(self):
        return self.entity_name


class Advocate(models.Model):
    advocate_id = models.AutoField(primary_key=True)
    advocate_name_first = models.CharField(max_length=50, blank=True, null=True)
    advocate_name_sur = models.CharField(max_length=50)
    advocate_name_others = models.CharField(max_length=100, blank=True, null=True)
    advocate_legalentity = models.ForeignKey(
        "LegalEntity",
        on_delete=models.PROTECT,
        db_column="advocate_legalentity",
        blank=True,
        null=True,
        related_name="advocates",
    )

    class Meta:
        db_table = "ci_advocates"
        managed = True
        constraints = [
            models.UniqueConstraint(
                fields=["advocate_name_first", "advocate_name_sur", "advocate_name_others"],
                name="ci_advocates_name_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["advocate_legalentity"], name="idx_ci_advocates_legalentity"),
        ]

    def __str__(self):
        parts = [
            self.advocate_name_first,
            self.advocate_name_sur,
            self.advocate_name_others,
        ]
        return " ".join(filter(None, parts)) or "Unnamed advocate"


# ============================================================
# Customers / retained parties
# ============================================================

class Customer(models.Model):
    class CustomerType(models.TextChoices):
        INDIVIDUAL = "Individual", "Individual"
        COMPANY = "Company", "Company"

    class IDType(models.TextChoices):
        NATIONAL_ID = "National ID", "National ID"
        PASSPORT = "Passport", "Passport"
        ALIEN_ID = "Alien ID", "Alien ID"

    customer_id = models.CharField(primary_key=True, max_length=8)
    customer_type = models.CharField(max_length=20, choices=CustomerType.choices)
    name_first = models.CharField(max_length=50, blank=True, null=True)
    name_sur = models.CharField(max_length=50, blank=True, null=True)
    name_others = models.CharField(max_length=100, blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)

    nationality_country = models.ForeignKey(
        "Country",
        on_delete=models.PROTECT,
        db_column="nationality_country_id",
        blank=True,
        null=True,
        related_name="customers_of_nationality",
    )
    residence_country = models.ForeignKey(
        "Country",
        on_delete=models.PROTECT,
        db_column="residence_country_id",
        blank=True,
        null=True,
        related_name="customers_resident_in",
    )

    phone_primary = models.CharField(max_length=16, blank=True, null=True)
    phone_secondary = models.CharField(max_length=16, blank=True, null=True)
    email = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        validators=[EmailValidator()],
    )
    name_company = models.CharField(max_length=100, blank=True, null=True)

    physical_address = models.CharField(max_length=100, blank=True, null=True)
    physical_locality = models.ForeignKey(
        "Locality",
        on_delete=models.PROTECT,
        db_column="physical_locality",
        blank=True,
        null=True,
        related_name="customers_physical",
    )
    physical_zip = models.CharField(max_length=10, blank=True, null=True)

    postal_address = models.CharField(max_length=100, blank=True, null=True)
    postal_locality = models.ForeignKey(
        "Locality",
        on_delete=models.PROTECT,
        db_column="postal_locality",
        blank=True,
        null=True,
        related_name="customers_postal",
    )
    postal_zip = models.CharField(max_length=10, blank=True, null=True)

    id_type = models.CharField(max_length=25, choices=IDType.choices, blank=True, null=True)
    id_number = models.CharField(max_length=30, blank=True, null=True)
    id_issue_date = models.DateField(blank=True, null=True)
    id_expiry_date = models.DateField(blank=True, null=True)
    id_scanfront = models.CharField(max_length=255, blank=True, null=True)
    id_scanback = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "ar_customers"
        managed = True
        constraints = [
            models.CheckConstraint(
                check=(
                    (Q(customer_type="Individual") & ~Q(name_first__isnull=True) & ~Q(name_sur__isnull=True))
                    | (Q(customer_type="Company") & ~Q(name_company__isnull=True))
                ),
                name="ar_customers_person_or_company",
            ),
            models.CheckConstraint(
                check=(
                    Q(id_issue_date__isnull=True)
                    | Q(id_expiry_date__isnull=True)
                    | Q(id_expiry_date__gte=F("id_issue_date"))
                ),
                name="ar_customers_id_dates",
            ),
        ]
        indexes = [
            models.Index(fields=["nationality_country"], name="idx_ar_customers_nationality_country_id"),
            models.Index(fields=["residence_country"], name="idx_ar_customers_residence_country_id"),
            models.Index(fields=["physical_locality"], name="idx_ar_customers_physical_locality"),
            models.Index(fields=["postal_locality"], name="idx_ar_customers_postal_locality"),
        ]

    def clean(self):
        super().clean()

        if self.customer_type == self.CustomerType.INDIVIDUAL:
            if not self.name_first or not self.name_sur:
                raise ValidationError("Individual customers must have first and surname names.")

        if self.customer_type == self.CustomerType.COMPANY:
            if not self.name_company:
                raise ValidationError("Company customers must have a company name.")

        if (
            self.id_issue_date
            and self.id_expiry_date
            and self.id_expiry_date < self.id_issue_date
        ):
            raise ValidationError("ID expiry date cannot be earlier than issue date.")

    def __str__(self):
        if self.customer_type == self.CustomerType.COMPANY:
            return self.name_company or self.customer_id
        full_name = f"{self.name_first or ''} {self.name_sur or ''}".strip()
        return full_name or self.customer_id


# ============================================================
# Case categories
# ============================================================

class CaseCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        db_column="parent_id",
        blank=True,
        null=True,
        related_name="children",
    )

    class Meta:
        db_table = "ci_case_categories"
        managed = True
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "category_name"],
                name="ci_case_categories_name_parent_unique",
            ),
            models.CheckConstraint(
                check=Q(parent__isnull=True) | ~Q(parent=F("category_id")),
                name="ci_case_categories_no_self_parent",
            ),
        ]

    def __str__(self):
        return self.category_name


# ============================================================
# Cases
# ============================================================

class Case(models.Model):
    class CaseStatus(models.TextChoices):
        ACTIVE = "Active", "Active"
        PENDING = "Pending", "Pending"
        STAYED = "Stayed", "Stayed"
        CONCLUDED = "Concluded", "Concluded"
        ARCHIVED = "Archived", "Archived"

    case_id = models.AutoField(primary_key=True)
    case_internal_reference_id = models.CharField(max_length=10, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(
        "Customer",
        on_delete=models.PROTECT,
        db_column="customer_id",
        blank=True,
        null=True,
        related_name="primary_cases",
    )
    forum = models.ForeignKey(
        "Forum",
        on_delete=models.PROTECT,
        db_column="forum_id",
        related_name="cases",
    )
    forum_case_number = models.CharField(max_length=50)
    date_forum_filing = models.DateField(blank=True, null=True)
    case_type = models.ForeignKey(
        "CaseCategory",
        on_delete=models.PROTECT,
        db_column="case_type",
        related_name="cases",
    )
    case_assigned_advocate = models.ForeignKey(
        "Advocate",
        on_delete=models.PROTECT,
        db_column="case_assigned_advocate",
        blank=True,
        null=True,
        related_name="assigned_cases",
    )
    claim_nature = models.TextField(blank=True, null=True)
    case_status = models.CharField(max_length=20, choices=CaseStatus.choices)

    class Meta:
        db_table = "ci_cases"
        managed = True
        constraints = [
            models.UniqueConstraint(
                fields=["forum", "forum_case_number"],
                name="ci_cases_forum_case_number_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["customer"], name="idx_ci_cases_customer_id"),
            models.Index(fields=["forum"], name="idx_ci_cases_forum_id"),
            models.Index(fields=["case_status"], name="idx_ci_cases_status"),
            models.Index(fields=["case_type"], name="idx_ci_cases_type"),
            models.Index(fields=["case_assigned_advocate"], name="idx_ci_cases_assigned_advocate"),
        ]

    def __str__(self):
        return self.case_internal_reference_id


# ============================================================
# Case parties / multi-client support
# ============================================================

class CaseCustomer(models.Model):
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(
        "Case",
        on_delete=models.PROTECT,
        db_column="case_id",
        related_name="case_customers",
    )
    customer = models.ForeignKey(
        "Customer",
        on_delete=models.PROTECT,
        db_column="customer_id",
        related_name="case_links",
    )
    role = models.CharField(
        max_length=50,
        choices=[
            ("Lead Plaintiff", "Lead Plaintiff"),
            ("Co-Plaintiff", "Co-Plaintiff"),
            ("Class Representative", "Class Representative"),
            ("Primary Client", "Primary Client"),
            ("Client", "Client"),
            ("Defendant", "Defendant"),
            ("Interested Party", "Interested Party"),
            ("Other", "Other"),
        ],
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "ci_case_customers"
        managed = True
        constraints = [
            models.UniqueConstraint(fields=["case", "customer"], name="ci_case_customers_unique"),
        ]
        indexes = [
            models.Index(fields=["customer"], name="idx_ci_case_customers_customer_id"),
            models.Index(fields=["role"], name="idx_ci_case_customers_role"),
        ]

    def __str__(self):
        return f"{self.case.case_internal_reference_id} / {self.customer.customer_id} / {self.role}"

# ============================================================
# Optional class entity (class actions / representative actions)
# ============================================================

class CaseClass(models.Model):
    class ClassStatus(models.TextChoices):
        ACTIVE = "Active", "Active"
        CERTIFIED = "Certified", "Certified"
        SETTLED = "Settled", "Settled"
        CLOSED = "Closed", "Closed"

    class_id = models.AutoField(primary_key=True)
    case = models.ForeignKey(
        "Case",
        on_delete=models.PROTECT,
        db_column="case_id",
        related_name="case_classes",
    )
    class_name = models.CharField(max_length=255)
    class_description = models.TextField(blank=True, null=True)
    class_status = models.CharField(
        max_length=30,
        choices=ClassStatus.choices,
        default=ClassStatus.ACTIVE,
    )

    class Meta:
        db_table = "ci_case_classes"
        managed = True
        constraints = [
            models.UniqueConstraint(
                fields=["case", "class_name"],
                name="ci_case_classes_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["case"], name="idx_ci_case_classes_case_id"),
        ]

    def __str__(self):
        return f"{self.case.case_internal_reference_id} / {self.class_name}"


class CaseOpposingAdvocate(models.Model):
    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(
        "Case",
        on_delete=models.PROTECT,
        db_column="case_id",
        related_name="opposing_advocates",
    )
    advocate = models.ForeignKey(
        "Advocate",
        on_delete=models.PROTECT,
        db_column="advocate_id",
        related_name="opposing_case_links",
    )
    role = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "ci_case_opposing_advocates"
        managed = True
        constraints = [
            models.UniqueConstraint(fields=["case", "advocate"], name="ci_case_opposing_advocates_unique"),
        ]
        indexes = [
            models.Index(fields=["advocate"], name="idx_ci_case_opposing_advocates_advocate_id"),
        ]

    def __str__(self):
        return f"{self.case.case_internal_reference_id} / {self.advocate_id}"


# ============================================================
# Case events
# ============================================================

class CaseEvent(models.Model):
    class EventType(models.TextChoices):
        HEARING = "Hearing", "Hearing"
        MENTION = "Mention", "Mention"
        RULING = "Ruling", "Ruling"
        SUBMISSION_DEADLINE = "Submission Deadline", "Submission Deadline"

    id = models.AutoField(primary_key=True)
    case = models.ForeignKey(
        "Case",
        on_delete=models.PROTECT,
        db_column="case_id",
        related_name="events",
    )
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    event_date = models.DateField()
    event_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ci_case_events"
        managed = True
        indexes = [
            models.Index(fields=["case", "event_date"], name="idx_ci_case_events_case_date"),
        ]

    def __str__(self):
        return f"{self.case.case_internal_reference_id} - {self.event_type}"


# ============================================================
# Mayan integration link
# ============================================================

class MayanCaseLink(models.Model):
    """
    This is intentionally a loose integration table.
    We do NOT force a hard FK to Case because the Mayan document
    metadata may outlive the legal case record in practice, or the
    link may be created before the case is finalized.
    """
    link_id = models.AutoField(primary_key=True)
    case_internal_reference_id = models.CharField(max_length=12, db_index=True)
    mayan_document_id = models.BigIntegerField()
    mayan_metadata_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mayan_case_links"
        managed = True
        constraints = [
            models.UniqueConstraint(
                fields=["case_internal_reference_id", "mayan_document_id", "mayan_metadata_key"],
                name="mayan_case_links_unique",
            ),
        ]
