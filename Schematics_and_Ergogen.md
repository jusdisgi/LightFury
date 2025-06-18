# How to make KiCad Schematics and Ergogen play nice!

## Why you should care
OK ergogen is great, right? (If you don't know about ergogen or why it's great, take a read through FlatFootFox's excellent [tutorial](https://flatfootfox.com/ergogen-introduction/) on the subject, then come back!) 
It lets you define keyboard layouts and nets programmatically in YAML, using footprints whose behavior you can change with parameters; who doesn't like that amirite?

But the thing is, KiCad schematics are *also* great! They let you define the electronics of your keyboard in a rigorous fashion, make it easier to understand, and enable a whole regime of error checking beyond what's possible in PCB files. Again, what's not to like?

Sadly, while ergogen happily generates KiCad PCB files, it does not create schematics. And if you create your own, unless you pay careful attention to setting it up to agree with ergogen, connecting/validating your schematic and PCB will break one or both of them.

Luckily, it *is* possible to make them sing in harmony. This document aims to tell you how.

## Shut up and tell me how to set it up!
Alright, can do. Just do this:

1. When building your schematic, make sure all the components have the same references that ergogen will give them.
2. Make sure all the pin numbers are the same in both places.
3. Use the same net labels in the same place in both ergogen and schematic.
4. After ergogen generates your PCB file, name it the same as your schematc (except the extension, duh).
5. Once you have both files, open the schematic, click "Tools -> Update Schematic From PCB", and check the boxes "Re-link footprints to schematic symbols based on their reference designators" and "Footprint assignments" leaving *all* other boxes unchecked.
6. Carefully check both schematic and PCB file for errors.
7. If you did everything right, the only thing that should have changed during step 6 was that you got a whole lot of labels added to the fab layer of your PCB. If so, congratulations, you now have a working schematic+ergogen+PCB combination.

That's the overview. But you should probably keep reading, because a few of those are trickier than they sound. I'm going to go through each one in a bit more detail.

## References and their Discontents
Each symbol in a KiCad schematic, and each footprint in a KiCad PCB, has a "Reference Designator" which must be unique within the document. When KiCad checks the PCB against the schematic or vice-versa, it expects these Refs to match up. If switch `S1` is 
connected to diode `D1` in the schematic, but connected to `D5` in the PCB, something bad will happen when you update. Same story if you have `SW1` in the schematic but `S1` in your PCB.

Ergogen creates a Ref for every component it puts into your PCB file. Knowing how it assigns them is critical to successfully building your schematic to match.

The short version of this is simple: the first, non-numeric part is defined in the "designator:" parameter to each footprint, and they are numbered in the order ergogen creates them.

To add a bit of detail to that: there is a default designator defined in each ergogen footprint file; for switches it is typically `S` for example. But you can override these in the `pcbs:` section of your ergogen config if you wish. The number, as I said, 
is in order of creation...which is determined through a combination of how your `pcbs:` and `points:` sections are organized. For some things that's simple: if you give your power switch and reset switch the same `designator:` param, whichever one occurs
first in the `pcbs:` section will have the lower number. The complexity begins when you give a footprint in your `pcbs:` section a more complex `where:` value, like for example your keyswitches. That's when the order of the points comes into play.

In a typical ergogen config, you will define your keyswitch footprint once, or perhaps twice, and use a `where:` that matches all (or half) of the points defined for keys in the `points:` section. In such a case, the references get assigned in the order of the
matching points. For keys, this is normally done by columns from left to right, with the keys in each column going bottom to top. So, in a typical five-column/three-row layout, the first key (`S1` by default) will be the bottom row pinky. `S2` will be pinky home, 
`S3` pinky top, `S4` ring bottom, and so on all the way to inner top which would be `S15`. Then the thumbs, which are typically defined after the finger keys, will be numbered starting from `S16` in the order they appear in the config.

That's really the main special case. Other things with complex `where:` in their footprint definition tend to be easy to figure out. If you have a mounting hole footprint with `where: /^screw/` and a big list of helper points named `screw_num_X` they will be ordered 
the same as you put the helper points in the file.

If you're ever confused about what order ergogen is going to assign references, you can always just have it generate the PCB and look. Selecting the footprint in the PCB file shows the Ref in the bottom left corner.

## Put a Pin (Number) in it
Each symbol in a KiCad schematic that has connection points (pins) includes an identifier (which is usually a number, but occasionally might not be, for example many mounting pads are labeled `MP`) for each pin in the symbol. These must correspond to the 
pads/pins/holes/etc. on your PCB footprints. This is not always obvious! In particular symbols may sometimes have these numbers set not to display. But once again, if you connect `P2` to a diode in your schematic and `P2` to that diode in your PCB, bad things 
will happen.

The best way to handle this is to always use symbols which show the pin numbers, and always be clear on which pins ergogen is using for what. You may need to generate the PCB file and have a look.

## Cast the Net on the Right Side of the Schematic, and Ye Shall Find
The last critical things that must match between PCB and schematic are the net labels. Technically, if everything else is setup right you could ignore this; when you update the schematic from the PCB, one or the other of them (depending which boxes you checked) 
will have its nets changed to match the other. But ideally you should just start by naming them all the same. If you do that, then after updating nothing should change in either place.

## The Electric KiCad Acid Test
If you've done all the above, your schematic is *almost* properly connected to your PCB. But not quite...the footprints associated to the symbols are wrong. This is because ergogen creates the KiCad footprints local within your PCB file when it runs; these footprints 
don't exist in your KiCad libraries at all. So the only way to get your schematic and PCB fully synced is to run the update tool. You should do this from within the schematic, using the option in the tools menu `Update Schematic from PCB` **NOT** the more commonly-used 
tool `Update PCB from Schematic`

When running this tool:
1. Check the box at the very top labeled `Re-link footprints to schematic symbols based on their reference designators`
2. In the section below check `Footprint assignments`
3. Usually you want to leave the other boxes unchecked. An exception is that you might wish to check `Net Names` if you're hoping to update your schematic nets from the PCB. But if you want the reverse (update nets in PCB to match schematic) leave it unchecked.
4. Read the box below those checkboxes carefully. It explains what changes will be made to the schematic...but be advised it does **NOT** say what's going to change in the PCB!

Did you just do a double-take there? I did. Yes, that's right...despite the tool being named "Update Schematic *from* PCB" it actually updates *both* files. And it **DOES NOT** say anything whatsoever about what it's going to do on the PCB side.

In my opinion that is a horrible design flaw. But nobody asked me. So we'll just have to work with it. There are a couple things you can do to try to mitigate this issue: 
1. Before updating your schematic, run DRC on your PCB file, checking the box "Test for Parity between PCB and Schematic"
2. Click the button for "Update PCB from Schematic" but *DO NOT* run the tool, just read the output to get an idea of what might change. Also you'll need to ignore any footprint mismatches.





