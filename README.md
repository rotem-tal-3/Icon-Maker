# Icon Maker

Command line tool to generate Chrome extension icons from a given source image. 
By default produces icons16/32/48/128.png with the respective sizes.

## Features
- Square export with two strategies:
  * contain (default): keep aspect ratio, pad to square with transparent or color bg
  * cover: center-crop to square before resizing
- Optional rounded edges
- Zips all outputs by default

## Dependencies
PIL 9.0.1

## Usage examples

Basic (contain-fit into square, transparent background)
```
python icon_maker.py -i face.png -o ./icons
```
Cover-crop to square first, then resize
```
python icon_maker.py -i face.png -o ./icons --mode cover
```

Use a solid background when padding (hex or css name understood by PIL)
```
python icon_maker.py -i face.png -o ./icons --bg "#0f172a"
```
Custom size set, no zip, make the images round
```
python icon_maker.py -i face.png -o ./icons --sizes 16 32 48 128 256 512 --no-zip --round
```
