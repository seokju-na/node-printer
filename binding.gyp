{
  "variables": {
    "module_name%": "node_printer",
    "module_path%": "lib/binding",
    "openssl_fips": "",
    # Node >= 24 common.gypi references this on Windows, but process.config of
    # older host Node (used by prebuild's node-gyp) doesn't define it.
    "enable_thin_lto%": "false"
  },
  'targets': [
    {
      "target_name": "action_after_build",
      "type": "none",
      "dependencies": [ "<(module_name)" ],
      "copies": [
        {
          "files": [ "<(PRODUCT_DIR)/<(module_name).node" ],
          "destination": "<(module_path)"
        }
      ]
    },
    {
      'target_name': '<(module_name)',
      'sources': [
        'src/node_printer.cc',
        'src/node_printer_win.cc',
        'src/node_printer_posix.cc'
      ],
      'include_dirs' : [
        "<!(node -e \"require('nan')\")",
        "src"
      ],
      'cflags_cc+': [
        "-Wno-deprecated-declarations",
        '-std=gnu++20'
      ],
      'conditions': [
        # common exclusions
        ['OS!="linux"', {'sources/': [['exclude', '_linux\\.cc$']]}],
        ['OS!="mac"', {'sources/': [['exclude', '_mac\\.cc|mm?$']]}],
        ['OS!="win"', {
          'sources/': [['exclude', '_win\\.cc$']]}, {
          # else if OS==win, exclude also posix files
          'sources/': [['exclude', '_posix\\.cc$']],
          # windows.h (pulled in via uv.h) defines min/max macros that break
          # std::numeric_limits<T>::max() in newer V8 headers (e.g. Electron 32).
          'defines': [ 'NOMINMAX' ]
        }],
        # specific settings
        ['OS!="win"', {
          'cflags':[
            '<!(cups-config --cflags)'
          ],
          'ldflags':[
            '<!(cups-config --libs)'
            #'-lcups -lgssapi_krb5 -lkrb5 -lk5crypto -lcom_err -lz -lpthread -lm -lcrypt -lz'
          ],
          'libraries':[
            '<!(cups-config --libs)'
            #'-lcups -lgssapi_krb5 -lkrb5 -lk5crypto -lcom_err -lz -lpthread -lm -lcrypt -lz'
          ],
          'link_settings': {
            'libraries': [
              '<!(cups-config --libs)'
            ]
          }
        }],
        ['OS=="mac"', {
          'cflags':[
            "-stdlib=libc++"
          ],
          'xcode_settings': {
            "OTHER_CPLUSPLUSFLAGS":["-std=c++20", "-stdlib=libc++"],
            "OTHER_LDFLAGS": ["-stdlib=libc++"],
            "MACOSX_DEPLOYMENT_TARGET": "10.7",
          },
        }],
      ]
    }
  ]
}
