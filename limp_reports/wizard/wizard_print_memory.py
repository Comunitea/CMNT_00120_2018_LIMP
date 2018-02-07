from openerp.osv import osv, fields
import time

class wizard_print_memory(osv.osv_memory):

    _name = "wizard.print.memory"
    _columns = {
        'year' : fields.integer('Year', required=True),
        'company_id':fields.many2one('res.company','Company',required=True),
    }
    _defaults = {
        'year' : lambda *x: int(time.strftime('%Y')),
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id,
    }

    def print_report(self, cr, uid, ids, context=None):
        """prints report"""
        if context is None:
            context = {}

        datas = {'ids': ids}
        datas['model'] = 'wizard.print.memory'
        datas['form'] = self.read(cr, uid, ids)[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'annual_memory',
            'datas': datas,
        }


wizard_print_memory()
