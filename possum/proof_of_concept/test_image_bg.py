#!/usr/bin/env python
import os
import elementary
import edje
import ecore
import evas


if __name__ == "__main__":
    def destroy(obj):
        elementary.exit()

    elementary.init()
    win = elementary.Window("image", elementary.ELM_WIN_BASIC)
    win.callback_destroy_add(destroy)
    win.title_set("Image")
    win.autodel_set(True)

    bg = elementary.Background(win)
    win.resize_object_add(bg)
    bg.file_set("/tmp/ca_par_jour.png")
    bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bg.show()

#    win.size_hint_min_set(160, 160)
#    win.size_hint_max_set(320, 320)
    win.resize(600, 400)
    win.show()
    elementary.run()
    elementary.shutdown()
