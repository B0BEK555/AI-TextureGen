# Minecraft texture generation winth AI
This is a small experiimental project, trying to make automated doodle to texture convertion.

### Textures in the `data/textures` come from Minecraft, or some specific Minecraft mods. We didn't make them

## Dataset
Currentli hand-drawig all doodles for the training dataset. Help would be appretiated.

## How to contribute
If you want to contribude to the doodle dataset, please follow these steps.

 - Clone the repository
 - Install python and all packages required for the painting app (pillow)
 - Run the "side_by_side.py"
 - Paint the doodles (more on that in the section below)
 - Pull-request the drawn doodles

## Painting rules
 - In the interface, select any mc tecture you want (just don't make the same texture over and over again)
 - Modded textures are allowed too, but make sure to choose a good vanilla style texture, and put it to the `data/textures` folder. Use only textures with the right license. Remember, the AI will be as good or as bad, as the textures that it's traind on
 - Paint any doodle style you want, as long as it is clearly recognizable to be the texture you tried to replicate
 - The shape should not be much shifted or rotated from the original texture
 - Try to paint something, that you would paint as an input for the fully trained AI, to make you the output texture (if you don't think that your doodle would get convereted to the right texture, it's a bad training doodle)
 - You can make multiple styles, filled, outlines, but the doodle must satisfy all the other rules (you can check the already existing doodles, if you are unsure what we mean)
