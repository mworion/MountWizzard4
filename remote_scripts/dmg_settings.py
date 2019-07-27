import biplist
import os.path

application = defines.get('app', '/Applications/TextEdit.app')
appname = os.path.basename(application)


def icon_from_app(app_path):
    plist_path = os.path.join(app_path, 'Contents', 'Info.plist')
    plist = biplist.readPlist(plist_path)
    icon_name = plist['CFBundleIconFile']
    icon_root,icon_ext = os.path.splitext(icon_name)
    if not icon_ext:
        icon_ext = '.icns'
    icon_name = icon_root + icon_ext
    return os.path.join(app_path, 'Contents', 'Resources', icon_name)


filename = './dist/MountWizzard4'
volume_name = 'MountWizzard4'
files = ['./dist/MountWizzard4.app']
symlinks = {'Applications': '/Applications'}
icon = icon_from_app(application)
badge_icon = icon_from_app(application)
icon_locations = {
    'MountWizzard4.app': (100, 100),
    'Applications': (300, 100)
}
background = '#104860'
# window_rect =
default_view = 'icon-view'
grid_spacing = 64
include_icon_view_settings = 'auto'
include_list_view_settings = 'auto'
