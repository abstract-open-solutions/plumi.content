from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('plumi.content')

security.declarePublic('ReTranscodePermission')
ReTranscodePermission = 'plumi.content: ReTranscode Video'
setDefaultRoles(ReTranscodePermission, ())
