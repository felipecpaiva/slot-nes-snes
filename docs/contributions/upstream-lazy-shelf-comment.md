Thanks again for the go-ahead on the NES/SNES patch set, it is very much appreciated.

While building it I found a small boot cost that also applies to upstream. `Shelf::new` reads a
header byte from every GB and GBC ROM to pick the faded-neighbour backing, but that value is only
needed when a faded cart is drawn. On my RG34XXSP with 854 GBC carts on the card, it is about
1.9 s of every boot. Making it lazy took scan to session from 1.87 s to 0.007 s, and the shelf
appeared at 2.04 s instead of 3.98 s (upstream 4a4ba92 against the same commit plus the change,
3 cold boots each, same card). The change is small, so I put it up as a PR: PR_LINK_PLACEHOLDER.
No hard feelings if you would rather do it another way.
