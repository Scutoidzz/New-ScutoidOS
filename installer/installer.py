#!/usr/bin/env python3
# ScutoidOS app installer - installs programs from programs/ into Apps/

import os
import shutil
import json
from datetime import datetime

class Installer:
    def __init__(self, base_path="/"):
        self.base = base_path
        self.apps_dir = os.path.join(base_path, "Apps")
        self.programs_dir = os.path.join(base_path, "programs")

        for d in [self.apps_dir, self.programs_dir,
                  os.path.join(base_path, "Users"),
                  os.path.join(base_path, "Other")]:
            os.makedirs(d, exist_ok=True)

    def scan_programs(self):
        found = []
        if not os.path.exists(self.programs_dir):
            return found

        for name in os.listdir(self.programs_dir):
            path = os.path.join(self.programs_dir, name)
            manifest = os.path.join(path, "app.json")

            if os.path.isdir(path) and os.path.exists(manifest):
                try:
                    with open(manifest, 'r') as f:
                        data = json.load(f)
                        data['path'] = path
                        data['name'] = data.get('name', name)
                        found.append(data)
                except Exception as e:
                    print(f"bad manifest in {name}: {e}")
            elif path.endswith('.py'):
                found.append({
                    'name': name.replace('.py', ''),
                    'type': 'standalone',
                    'path': path,
                    'main': name,
                    'description': 'standalone script'
                })
        return found

    def list_available(self):
        apps = self.scan_programs()
        if not apps:
            print("nothing to install.")
            return []

        print("\n--- available programs ---")
        for i, app in enumerate(apps, 1):
            desc = app.get('description', '')
            ver = app.get('version', '?')
            print(f"  {i}. {app['name']} (v{ver}) - {desc}")
        print()
        return apps

    def install(self, manifest):
        name = manifest['name']
        app_type = manifest.get('type', 'application')

        bundle_path = os.path.join(self.apps_dir, name)

        print(f"\n installing {name}...")

        if os.path.exists(bundle_path):
            shutil.rmtree(bundle_path)

        os.makedirs(bundle_path, exist_ok=True)

        if app_type == 'standalone':
            shutil.copy(manifest['path'], bundle_path)
            main_file = manifest['main']
        else:
            src = manifest['path']
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(bundle_path, item)
                if os.path.isfile(s):
                    shutil.copy(s, d)
                elif os.path.isdir(s):
                    shutil.copytree(s, d)
            main_file = manifest.get('main', 'main.py')

        info = {
            'name': name,
            'display_name': manifest.get('display_name', name),
            'identifier': f"org.scutoidos.{name.lower().replace(' ', '')}",
            'version': manifest.get('version', '1.0.0'),
            'executable': main_file,
            'installed': datetime.now().isoformat(),
            'description': manifest.get('description', ''),
            'author': manifest.get('author', 'unknown')
        }

        with open(os.path.join(bundle_path, "info.json"), 'w') as f:
            json.dump(info, f, indent=2)

        print(f" -> {bundle_path}")
        print(f"    entry: {main_file}")
        return bundle_path

    def list_installed(self):
        if not os.path.exists(self.apps_dir):
            print("no apps installed.")
            return []

        apps = []
        for item in os.listdir(self.apps_dir):
            path = os.path.join(self.apps_dir, item)
            info_path = os.path.join(path, "info.json")
            if os.path.isdir(path) and os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    info = json.load(f)
                    apps.append({'name': info.get('name', item), 'path': path, 'info': info})

        if not apps:
            print("no apps installed.")
            return []

        print("\n--- installed apps ---")
        for i, app in enumerate(apps, 1):
            info = app['info']
            print(f"  {i}. {info.get('display_name', app['name'])} v{info.get('version', '?')}")
        print()
        return apps

    def uninstall(self, name):
        path = os.path.join(self.apps_dir, name)
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
            print(f"removed {name}")
            return True
        print(f"not found: {name}")
        return False

    def interactive_install(self):
        apps = self.list_available()
        if not apps:
            return

        try:
            choice = input("pick a number (q to cancel): ").strip()
            if choice.lower() == 'q':
                return
            idx = int(choice) - 1
            if 0 <= idx < len(apps):
                self.install(apps[idx])
                print("done.")
            else:
                print("bad selection")
        except ValueError:
            print("bad input")
        except KeyboardInterrupt:
            print("\ncancelled.")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    base = os.path.dirname(here)

    inst = Installer(base)

    print("ScutoidOS Installer")
    print("=" * 35)

    while True:
        print("\n1. list available")
        print("2. list installed")
        print("3. install")
        print("4. uninstall")
        print("5. install all")
        print("6. quit")

        choice = input("\n> ").strip()

        if choice == '1':
            inst.list_available()
        elif choice == '2':
            inst.list_installed()
        elif choice == '3':
            inst.interactive_install()
        elif choice == '4':
            name = input("app name: ").strip()
            inst.uninstall(name)
        elif choice == '5':
            apps = inst.scan_programs()
            for app in apps:
                inst.install(app)
            print(f"\ninstalled {len(apps)} apps")
        elif choice in ('6', 'q'):
            break
        else:
            print("?")

if __name__ == "__main__":
    main()
