from plone import api


def import_profile(profile):
    setup = api.portal.get_tool('portal_setup')
    setup.runAllImportStepsFromProfile(profile)


def run_import_step_from_profile(
    context, step, module='seantis.people', profile='default'
):
    setup = api.portal.get_tool('portal_setup')
    profile = 'profile-{}:{}'.format(module, profile)
    setup.runImportStepFromProfile(profile, step)


def install_custom_controlpanel(context):
    run_import_step_from_profile(context, 'controlpanel')


def upgrade_phz_type_info(context):
    run_import_step_from_profile(context, 'typeinfo', 'seantis.people', 'phz')


def install_membership_dependencies(context):
    import_profile('profile-plone.formwidget.autocomplete:default')
    import_profile('profile-plone.app.relationfield:default')
