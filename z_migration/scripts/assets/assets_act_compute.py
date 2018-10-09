"""
This method will click button compute in assets
"""
import sys
import os
try:
    asset_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.dirname(asset_path)
    migration_path = os.path.dirname(script_path)
    controller_path = '%s/controller' % migration_path
    sys.path.insert(0, controller_path)
    from connection import connection
    import log
except Exception:
    pass

# Model
Asset = connection.get_model('account.asset')

# Domain
# asset_codes = ['7440-028-0001-000000003']
# dom = [('code', 'in', asset_codes)]
dom = [('state', '=', 'draft')]

# Search Asset
assets = Asset.search_read(dom)

log_asset_ids = [[], []]
logger = log.setup_custom_logger('assets_act_compute')
logger.info('Start process')
logger.info('Total asset: %s' % len(assets))
for asset in assets:
    try:
        Asset.mork_compute_depreciation_board([asset['id']])
        log_asset_ids[0].append(asset['id'])
        logger.info('Pass ID: %s' % asset['id'])
    except Exception as ex:
        log_asset_ids[1].append(asset['id'])
        logger.error('Fail ID: %s (reason: %s)' % (asset['id'], ex))
summary = 'Summary: pass %s%s and fail %s%s' \
          % (len(log_asset_ids[0]),
             log_asset_ids[0] and ' %s' % str(tuple(log_asset_ids[0]))
             or '', len(log_asset_ids[1]),
             log_asset_ids[1] and ' %s' % str(tuple(log_asset_ids[1]))
             or '')
logger.info(summary)
logger.info('End process')
