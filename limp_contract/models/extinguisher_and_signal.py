from odoo import models, fields, _, api


class ExtinguisherAndSignal(models.Model):
    _name = 'extinguisher.and.signal'
    _description = 'Signal and extinguisher information'

    name = fields.Char(
        'Name',
        compute='_compute_name',
        store=True,
        readonly=True,
        default=_("New Extinguisher and signal"),
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
    re_embossed_date = fields.Date(
        'Re-embossed date',
        compute='_compute_extiguisher_dates',
        store=True,
        readonly=False,
    )
    revision_date = fields.Date(
        'Revision date',
        compute='_compute_extiguisher_dates',
        store=True,
        readonly=False,)
    extinguisher_type = fields.Char(
        'Extinguisher Type',
        readonly=True,
        compute='_compute_extinguisher_type',
        store=True
    )
    extinguisher_agent = fields.Selection([
        ('co2', 'CO2'),
        ('dust_abc', 'Dust ABC'),
        ('afff', 'AFFF'),
    ], 'Extinguisher agent')
    weight = fields.Float('Weight', required=True)
    preasure_ok = fields.Boolean('Preasure OK')
    pressure = fields.Float('Pressure')
    extinguisher_signal_manufacturing_date = fields.Date('Signal Manufacturing date', required=True)
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

    @api.depends('brand', 'model', 'plate_num', 'contract_id')
    def _compute_name(self):
        for record in self:
            if record.brand and record.model and record.plate_num:
                name = record.brand + " " + record.model + " " + record.plate_num
            else:
                name = _("New Extinguisher and signal")
            record.name = name

    def _get_date(self, test_type):
        self.ensure_one()
        self_id = self.id
        picking_ids = self.contract_id.stock_maintenace_service_picking_ids.filtered(
            lambda x: x.has_extinguisher_revision is True
        ).mapped('extinguisher_revision_ids').filtered(
            lambda x: x.extinguisher_and_signal_id.id == self_id
            and x.test_type == test_type
        ).mapped('stock_service_picking_id').sorted(key='picking_date', reverse=True)
        if picking_ids:
            return picking_ids[0].picking_date
        else:
            return False

    @api.depends('contract_id', 'contract_id.stock_maintenace_service_picking_ids')
    def _compute_extiguisher_dates(self):
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

    @api.depends('weight', 'extinguisher_type')
    def _compute_extinguisher_type(self):
        for record in self:
            if not record.weight:
                continue
            if record.extinguisher_agent == 'co2':
                record.extinguisher_type = _('%s Kg CO2') % record.weight
            elif record.extinguisher_agent == 'dust_abc':
                record.extinguisher_type = _('%s Kg Dust ABC') % record.weight
            elif record.extinguisher_agent == 'afff':
                record.extinguisher_type = _('%s Kg AFFF') % record.weight


class ExtinguisherRevision(models.Model):
    _name = 'extinguisher.revision'
    _description = 'Extinguisher revision'

    extinguisher_and_signal_id = fields.Many2one(
        'extinguisher.and.signal',
        'Extinguisher and signal',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer('Sequence', related='extinguisher_and_signal_id.sequence', readonly=True)
    plate_num = fields.Char('Plate num', related='extinguisher_and_signal_id.plate_num', readonly=True)
    stock_service_picking_id = fields.Many2one(
        'stock.service.picking',
        'Service picking',
        readonly=True
    )
    location_id = fields.Many2one(
        'building.site.services.location',
        'Location',
        related='extinguisher_and_signal_id.location_id',
        readonly=True
    )
    test_type = fields.Selection([
        ('revision', 'Revision'),
        ('retire', 'Retire'),
        ('re_embossed', 'Re-embossed'),
    ], 'Test type')

    # CAMPOS DE LA REVISIÓN
    extinguisher_is_visible = fields.Boolean('Extinguisher is visible')  # 1.1
    extinguisher_is_accesible = fields.Boolean('Extinguisher is accesible')  # 1.2
    extinguisher_situacion_correct = fields.Boolean('Extinguisher situation correct')  # 1.3
    extinguisher_adecuate_signaling = fields.Boolean('Extinguisher adecuate signaling')  # 1.4
    extinguisher_correct_support = fields.Boolean('Extinguisher correct support')  # 1.5
    extinguisher_correct_height = fields.Boolean('Extinguisher correct height')  # 1.6
    extinguisher_correct_aspect = fields.Boolean('Extinguisher correct aspect')  # 1.7
    extinguisher_correct_precint_seal = fields.Boolean('Extinguisher correct precint / seal')  # 1.8
    extinguisher_available_aperture_indicative = fields.Boolean('Extinguisher available aperture indicative')  # 1.9
    extinguisher_correct_identification_tag = fields.Boolean('Extinguisher correct identification and tag')  # 1.10
    extinguisher_correct_identification_mantainance_tag = fields.Boolean(
        'Extinguisher correct identification and mantainance tag'
    )  # 1.11
    extinguisher_3kg_has_hose = fields.Boolean('Extinguisher 3kg has hose')  # 1.12
    extinguisher_correct_hose = fields.Boolean('Extinguisher correct hose')  # 1.13
    extinguisher_correct_valve = fields.Boolean('Extinguisher correct valve')  # 1.14
    extinguisher_correct_charge_weight = fields.Boolean('Extinguisher correct charge using weight')  # 1.15
    extinguisher_correct_agent_state = fields.Boolean('Extinguisher correct agent state')  # 1.16
    extinguisher_correct_normative_mark = fields.Boolean('Extinguisher correct normative mark')  # 1.17
    extinguisher_correct_re_embossed_normative_pressure_devices = fields.Boolean(
        'Extinguisher correct re-embossed by the normative pressure devices'
    )  # 1.18
    extinguisher_correct_charge_weight_attached_pressure = fields.Boolean(
        'Extinguisher correct charge weight attached to pressure'
    )  # 1.19
    extinguisher_correct_re_embossed_normative_pressure = fields.Boolean(
        'Extinguisher correct re-embossed by the normative pressure'
    )  # 1.20
    extinguisher_correct_interior_pressure = fields.Boolean('Extinguisher correct interior pressure')  # 1.21
    substitution_stinguisher_correct = fields.Boolean('Substitution stinguisher correct')  # E.S.
    extinguisher_workshop_retirement = fields.Boolean('Extinguisher workshop retirement')  # R.T.
    revision_result = fields.Text('Revision result')
    revision_date = fields.Date('Revision date')
