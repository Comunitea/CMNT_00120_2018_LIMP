from odoo import models, fields, api, _


class BIEAndSignal(models.Model):
    _name = 'bie.and.signal'
    _description = 'Bie and signal'

    name = fields.Char(
        'Name',
        compute='_compute_name',
        store=True,
        readonly=True,
        default=_("New BIE and signal"),
        force_save=True
    )

    sequence = fields.Integer('Sequence', required=True)
    brand = fields.Char('Brand', required=True)
    model = fields.Text('Model',)
    plate_num = fields.Char('Plate num', required=True)
    manufacturing_date = fields.Date(
        'Manufacturing date',
        required=True,
    )
    weight = fields.Float('Weight')
    bie_type = fields.Char(
        'BIE Type'
    )
    re_embossed_date = fields.Date('Re-embossed date',)
    bie_extinguisher_agent = fields.Char('Extinguisher agent')
    revision_date = fields.Date(
        'Revision date',
        compute='_compute_bie_dates',
        store=True,
        readonly=False,
    )
    preasure_ok = fields.Boolean('Preasure OK')
    pressure = fields.Float('Pressure')
    bie_signal_manufacturing_date = fields.Date('Signal Manufacturing date', required=True)
    signal_observation_ok = fields.Boolean('Signal observation OK')
    signal_observation = fields.Text('Signal observation')
    signal_test_type = fields.Selection([
        ('revision', 'Revision'),
    ], 'Signal test type')
    building_site_id = fields.Many2one(
        'building.site.services',
        'Building site',
    )
    location_id = fields.Many2one(
        'building.site.services.location',
        'Location',
        domain="[('building_site_services_id', '=', building_site_id)]"
    )
    contract_id = fields.Many2one('limp.contract', 'Service picking', required=True)

    def _get_date(self, test_type):
        self.ensure_one()
        picking_ids = self.contract_id.stock_maintenace_service_picking_ids.filtered(
            lambda x: x.has_bie_revision is True
        ).mapped('bie_revision_ids').filtered(
            lambda x: x.bie_and_signal_id.id == self.id
            and x.test_type == test_type
        ).mapped('stock_service_picking_id').sorted(key='picking_date', reverse=True)
        if picking_ids:
            return picking_ids[0].picking_date
        else:
            return False

    @api.depends('contract_id', 'contract_id.stock_maintenace_service_picking_ids')
    def _compute_bie_dates(self):
        for record in self:
            re_embossed_date = record._get_date('re-embozed')
            if re_embossed_date or not record.re_embossed_date:
                record.re_embossed_date = re_embossed_date
            else:
                record.re_embossed_date = record.re_embossed_date

            revision_date = record._get_date('revision')
            if revision_date is not False or record.revision_date is False:
                record.revision_date = revision_date
            else:
                record.revision_date = record.revision_date

    @api.depends('brand', 'model', 'plate_num')
    def _compute_name(self):
        for record in self:
            if record.brand and record.model and record.plate_num and record.contract_id:
                name = record.brand + " " + record.model + " " + record.plate_num
            else:
                name = _("New BIE and signal")
            record.name = name


class BIERevision(models.Model):
    _name = 'bie.revision'
    _description = 'BIEs revision'

    bie_and_signal_id = fields.Many2one(
        'bie.and.signal',
        'BIE and signal',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer('Sequence', related='bie_and_signal_id.sequence', readonly=True)
    plate_num = fields.Char('Plate num', related='bie_and_signal_id.plate_num', readonly=True)
    stock_service_picking_id = fields.Many2one(
        'stock.service.picking',
        'Service picking',
        readonly=True
    )
    location_id = fields.Many2one(
        'building.site.services.location',
        'Location',
        related='bie_and_signal_id.location_id',
        readonly=True
    )
    test_type = fields.Selection([
        ('revision', 'Revision'),
        ('retire', 'Retire'),
        ('re_embossed', 'Re-embossed'),
    ], 'Test type')

    # CAMPOS DE LA REVISIÓN
    bie_is_visible = fields.Boolean('BIE is visible')  # 1.1
    bie_is_accesible = fields.Boolean('BIE is accesible')  # 1.2
    bie_is_less_50 = fields.Boolean('BIE is at less than 50m from another')  # 1.3
    bie_valve_1_5_ground = fields.Boolean('BIE valve is at max 1.5 m from ground')  # 1.4
    bie_corrossion_free = fields.Boolean('BIE corrosion free')  # 1.5
    bie_precint_glass_intact = fields.Boolean('BIE precint glass')  # 1.6
    bie_correct_certification = fields.Boolean('BIE correct certification')  # 1.7
    bie_correct_pressure_gauge = fields.Boolean('BIE correct pressure gauge')  # 1.8
    bie_correct_hose = fields.Boolean('BIE correct hose')  # 1.9
    bie_is_clean = fields.Boolean('BIE is clean')  # 1.10
    bie_correct_hinge_locking = fields.Boolean('BIE correct hinge locking')  # 1.11
    bie_25_mm_correct_extraction_orientation = fields.Boolean('BIE of 25mm correct extraction_orientation')  # 1.12
    bie_45mm_couplings_are_certified = fields.Boolean('BIE 45mm couplings are certified')  # 1.13
    bie_45mm_couplings_joints_correct = fields.Boolean('BIE 45mm couplings and joints are correct')  # 1.14
    bie_correct_nozzle = fields.Boolean('BIE correct nozzle')  # 1.15
    bie_45mm_has_pressure_gauge = fields.Boolean('BIE 45mm has preasure gauge')  # 1.16
    bie_correct_normative_mark = fields.Boolean('BIE correct normative mark')  # 1.17
    bie_25mm_has_correct_pressure_gauge = fields.Boolean('BIE 25mm has correct pressure gauge')  # 1.18
    bie_25mm_has_correct_couplings_joints = fields.Boolean('BIE 25mm has correct couplings joints')  # 1.19
    bie_25mm_intake_45_certified_couplings = fields.Boolean('BIE 25mm has intake 45 and certified couplings')  # 1.20
    bie_correct_pressure_test = fields.Boolean('BIE correct pressure test')  # 1.21
    substitution_stinguisher_correct = fields.Boolean('Substitution BIE correct')  # E.S.
    bie_workshop_retirement = fields.Boolean('BIE workshop retirement')  # R.T.
    revision_result = fields.Text('Revision result')
    revision_date = fields.Date('Revision date')
