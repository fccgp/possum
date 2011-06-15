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
    bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    bg.show()
#    bg = elementary.Background(win)
#    win.resize_object_add(bg)
#    bg.file_set("/tmp/ca_par_jour.png")
#    bg.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
#    bg.show()

    image = elementary.Image(win)
#    #image.size_set(300, 500)
#    image.resize(600, 400)
    image.file_set("/tmp/ca_par_jour.png")
#    #image.size_hint_aspect_set(evas.EVAS_ASPECT_CONTROL_BOTH, 1, 1)
    image.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
    image.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
#    #icon.scale_set(0, 0)
#    #win.resize_object_add(icon)
#    tb.pack(image, 0, 3, 7, 3)
    image.show()
    win.resize_object_add(image)

#    win.size_hint_min_set(160, 160)
#    win.size_hint_max_set(320, 320)
    win.resize(1024, 768)
    win.show()
    elementary.run()
    elementary.shutdown()
