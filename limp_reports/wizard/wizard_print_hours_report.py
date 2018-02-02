from osv import fields, osv
import time
from tools.translate import _
import calendar
from datetime import datetime

MONTHS = [
    ('1', _("January")),
    ('2', _("February")),
    ('3', _("March")),
    ('4', _("April")),
    ('5', _("May")),
    ('6', _("June")),
    ('7', _("July")),
    ('8', _('August')),
    ('9', _("September")),
    ('10', _("October")),
    ('11', _("November")),
    ('12', _("December"))
]

class wizard_print_hours_reports(osv.osv_memory):

    _name = "wizard.print.hours.report"

    _columns = {
        'year' : fields.integer('Year', required=True),
        'month':fields.selection(selection=MONTHS,string='Month',required=True),
        'holiday_text': fields.text('Holidays', readonly=True)
    }
    _defaults = {
        'year' : lambda *x: int(time.strftime('%Y')),
        # 'company_id': lambda *x: str(int(time.strftime('%m'))), MIGRACION: Campo eliminado
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None: context = {}

        datas = {'ids': context['active_ids']}
        datas['model'] = 'limp.contract'
        datas['form'] = self.read(cr, uid, ids)[0]
        print datas
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'contract_hours_report',
            'datas': datas,
        }

    def on_change_month(self, cr, uid, ids, month, year, context=None):
        if context is None: context = {}
        txt = u""
        if context.get('active_ids', []) and month and year:
            start_date = datetime(int(year),int(month),1).strftime("%Y-%m-%d")
            end_date = datetime(int(year),int(month),calendar.monthrange(int(year), int(month))[1]).strftime("%Y-%m-%d")
            for contract in self.pool.get('limp.contract').browse(cr, uid, context['active_ids']):
                txt += contract.name + u"\n"
                occupations_ids = self.pool.get('account.analytic.occupation').search(cr, uid, [('analytic_account_id', 'child_of', contract.analytic_account_id.id), ('date', '>=', start_date), ('date', '<=', end_date), ('state', 'in', ['active', 'replacement'])])
                contract_holidays = []
                if occupations_ids:
                    occupation = self.pool.get('account.analytic.occupation').read(cr, uid, occupations_ids[0], ['employee_id', 'date', 'location_id', 'state_id', 'region_id'])

                    for holiday in self.pool.get('hr.holiday').get_holidays_dates(cr, uid, [occupation['employee_id'][0]], occupation.get('location_id', False) and occupation['location_id'][0] or False, occupation.get('state_id', False) and occupation['state_id'][0] or False, occupation.get('region_id', False) and occupation['region_id'][0] or False)[occupation['employee_id'][0]]:
                        if holiday >= start_date and holiday <= end_date:
                            contract_holidays.append(datetime.strptime(holiday, "%Y-%m-%d").strftime("%d-%m-%Y"))
                if contract_holidays:
                    txt += u", ".join(contract_holidays) + u"\n"
        return {'value': {'holiday_text': txt}}

wizard_print_hours_reports()
