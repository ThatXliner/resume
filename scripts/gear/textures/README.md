# Grip surface maps

`Leather037_NormalGL.png` and `Leather037_Roughness.png` are the unmodified
1K PNG maps from ambientCG Leather 037, captured using photometric stereo.

Source: https://ambientcg.com/view?id=Leather037
Download: https://ambientcg.com/get?file=Leather037_1K-PNG.zip
License: Creative Commons CC0 1.0 Universal.
License information: https://docs.ambientcg.com/license/

Only surface orientation and roughness are used; the camera retains its black
rubber base color. This is a reference-matched material approximation, not a
scan of Canon's actual grip rubber. Painted metal retains a separate material.

The build derives camera-grip roughness as `0.52 + 0.35 × source roughness`;
the source leather's unadjusted finish was too glossy in the viewer. Normal
strength is increased to represent the deeper molded grip texture, and both
maps share 1.25 repeats. Original downloaded files remain unchanged.

Grip UVs are normalized by world surface area after unwrapping: a texture square
covers 1.4 scene units before viewer repetition (55 mm per scene unit). This
keeps grain size consistent across the hand grip, front panel and thumb pad.
