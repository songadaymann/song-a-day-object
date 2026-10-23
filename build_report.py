# Copyright (C) 2026 Jonathan Mann
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate the illustrated brief and PNG comparison from completed Blender renders."""
import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parent
RENDERS = ROOT / 'renders'
concepts = json.loads((ROOT / 'research/concepts.json').read_text())
sources = json.loads((ROOT / 'research/sources.json').read_text())['sources']
source_by_id = {s['id']: s for s in sources}
with (ROOT / 'research/components.csv').open() as f:
    parts = list(csv.DictReader(f))
custom = [p for p in parts if p['route'] == 'Custom 100']
custom_total = sum(float(p['unit_usd']) for p in custom)

for c in concepts:
    assert (RENDERS / c['file']).exists(), c['file']


def font(size, bold=False):
    for name in (['Arial Bold.ttf', 'DejaVuSans-Bold.ttf'] if bold else ['Arial.ttf', 'DejaVuSans.ttf']):
        try: return ImageFont.truetype(name, size)
        except OSError: pass
    return ImageFont.load_default(size=size)


def compare_png():
    im = Image.new('RGB', (2400, 1880), '#f5f1e8')
    d = ImageDraw.Draw(im)
    d.text((65, 43), 'Song A Day, made physical.', fill='#172522', font=font(70, True))
    d.text((68, 137), 'Six Blender studies. One permanent song. One mute / unmute button.',
           fill='#34413a', font=font(25))
    cellw, cellh = 744, 715
    for i, c in enumerate(concepts):
        x = 66 + (i % 3) * 766
        y = 211 + (i // 3) * 779
        pic = Image.open(RENDERS / c['file']).convert('RGB')
        pic.thumbnail((cellw, 628), Image.Resampling.LANCZOS)
        im.paste(pic, (x + (cellw-pic.width)//2, y))
        d.text((x, y+650), c['id']+'  '+c['name'], font=font(38, True), fill='#172522')
        dims = ' x '.join(str(v) for v in c['dimensions'])+' mm'
        d.text((x, y+705), dims, font=font(25), fill='#34413a')
    d.line((67, 1806, 2334, 1806), fill='#25352d', width=2)
    d.text((67, 1825), 'W x D x H  |  Illustrative screen image  |  Concept envelopes, not fabrication CAD',
           font=font(25), fill='#34413a')
    im.save(ROOT / 'song-a-day-six-concepts.png')


compare_png()

W, H = 792, 612
INK = colors.HexColor('#172522')
ACCENT = colors.HexColor('#a84d31')
GREEN = colors.HexColor('#66825b')
PAPER = colors.HexColor('#f5f1e8')
RULE = colors.HexColor('#b3b4a4')
c = canvas.Canvas(str(ROOT / 'song-a-day-design-and-sourcing.pdf'), pagesize=(W, H))
c.setTitle('Song A Day object - designs, parts and power')
c.setAuthor('Jonathan Mann / Song A Day')
page_num = 0


def para(value, x, top, width, size=13, bold=False, color=INK):
    style = ParagraphStyle('p', fontName='Helvetica-Bold' if bold else 'Helvetica',
                           fontSize=size, leading=size*1.34, textColor=color,
                           spaceAfter=0, allowWidows=0, allowOrphans=0)
    p = Paragraph(value, style)
    _, hh = p.wrap(width, 1000)
    if top > 45 and top-hh < 43:
        print('LAYOUT WARNING', page_num, round(top-hh,1), value[:85], flush=True)
    p.drawOn(c, x, top-hh)
    return top-hh


def page(title, note=None):
    global page_num
    if page_num: c.showPage()
    page_num += 1
    c.setFillColor(PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)
    para(title, 36, 576, 720, 27, True)
    if note: para(note, 36, 537, 720, 10)
    c.setStrokeColor(RULE); c.setLineWidth(.6); c.line(36, 37, 756, 37)
    para('Song A Day object | October 23, 2026', 36, 28, 600, 10)
    c.setFont('Helvetica', 10); c.setFillColor(INK); c.drawRightString(756, 17, str(page_num))


def imagefit(path, x, y, width, height):
    im = Image.open(path)
    iw, ih = im.size
    scale = min(width/iw, height/ih)
    ww, hh = iw*scale, ih*scale
    c.drawImage(str(path), x+(width-ww)/2, y+(height-hh)/2, ww, hh,
                preserveAspectRatio=True, mask='auto')


def link_source(sid, label=None):
    s = source_by_id[sid]
    return '<a href="'+escape(s['url'], {'"':'&quot;'})+'" color="#a84d31">'+escape(label or sid)+'</a>'


def table(headers, rows, widths, x, top, size=10):
    st = ParagraphStyle('t', fontName='Helvetica', fontSize=size, leading=size*1.25, textColor=INK)
    sh = ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=size, leading=size*1.25, textColor=INK)
    vals = [[Paragraph(str(s), sh) for s in headers]]
    vals += [[Paragraph(str(s), st) for s in row] for row in rows]
    t = Table(vals, colWidths=widths, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LINEBELOW',(0,0),(-1,0),1,INK),
        ('LINEBELOW',(0,1),(-1,-1),.35,RULE),
    ]))
    _, hh = t.wrap(sum(widths), 1000)
    if top-hh < 43:
        print('TABLE WARNING', page_num, round(top-hh,1), headers, flush=True)
    t.drawOn(c, x, top-hh)
    return top-hh


page('Song A Day, made physical.')
y=para('A collectible that keeps one song present.',36,513,283,13,True)
y=para('A small object on a shelf. Its video loops continuously. One button brings the sound in and out. No menu, browsing or daily network dependency.',36,y-18,283)
y=para('<b>Start with Monolith.</b><br/>Matte black polymer, a deliberately coarse two-color picture, and a quiet mono speaker. Run it from discreet 5 V USB power.',36,y-24,283)
y=para('The sourced prototype is close to the requested price in bare parts. A finished, assembled object below $30 is still a cost-down target.',36,y-24,283)
imagefit(RENDERS/'01_monolith.png',333,150,423,385)
para('Working assumption: each collectible holds one permanently assigned song. A new song every day would add networking, setup and a different product lifecycle.',36,133,720,10)
para('This package contains six Blender studies, editable geometry, sourced components and power calculations. These are visual envelope studies; no circuit, firmware or acoustic performance has been bench-tested.',36,89,720,10)

page('Six objects for the same song', 'All dimensions are millimetres, W x D x H. Two-color imagery is simulated on a color TFT; the illustration is not a real video frame.')
for i,a in enumerate(concepts):
    x=36+(i%3)*244
    y=321 if i<3 else 96
    imagefit(RENDERS/a['file'],x,y,232,186)
    para(a['id']+' '+a['name'],x,y-3,232,13,True)
    para(' x '.join(map(str,a['dimensions']))+' mm',x,y-23,232,10)

page('Parts you can actually source', 'USD prices checked October 23, 2026. Published/indexed prices are references; taxes, shipping, tariff and final variant selection are extra.')
bottom=table(['Route','Main part','Published price','What it buys / open issue'],[
    ['Fast prototype','Waveshare ESP32-S3-LCD-2.8', '$19.99-$25.99 '+link_source('S01'),
     'Non-touch version is the low-price candidate. Screen, controller, card slot and audio are integrated. Confirm checkout variant. '+link_source('S02')],
    ['Smaller alternative','Elecrow CrowPanel Advance 2.4', 'From $19.90 '+link_source('S03'),
     'ESP32-S3, speaker port and storage. Vendor text conflicts on resolution; verify SKU before choosing it.'],
    ['Custom production','EastRising 2.4-inch display + custom board','$5.71 panel at 100 '+link_source('S04'),
     'A smaller display gives layout freedom and a cost-down path. Electronics design, assembly and firmware remain to be done.'],
    ['Reflective upgrade','Sharp LS027B7DH01A','$29.29 panel alone '+link_source('S10'),
     'True monochrome without a backlight. Already consumes almost the entire build budget before electronics or sound.']
], [100,178,123,319],36,510)
para('The smallest first purchase',36,bottom-24,720,13,True)
bot=table(['Item','USD','Source / qualification'],[
    ['Waveshare board, with its supplied 8-ohm speaker','$19.99',link_source('S01')+' - low-end non-touch listing; confirm selection'],
    ['128MB microSD for the fixed song','$3.95',link_source('S09')+' - published one-off, in stock'],
    ['Bare playback kit subtotal','$23.94','No enclosure, external mute button or USB cable yet'],
    ['Shell, mute switch/cap, wiring and USB lead','$7-$15','Planning allowance; enclosure and mechanical parts not quoted'],
], [320,75,325],36,bottom-46)
para('<b>Basic enclosed prototype: about $31-$39 in parts.</b> Add $4.94 to audition the 40 mm PUI speaker, making that version about $36-$44. Labour and AC power supply are extra. '+link_source('S07'),36,bot-15,720,10)

page('Can it cost $30?', 'A 100-unit custom-board estimate. Uses a 2.4-inch screen, not the larger 2.8-inch Waveshare module. Allowances are not factory quotes.')
rows=[]
for p in custom:
    name=p['role']
    qual=link_source(p['source_id']) if p['source_id'] else 'Allowance'
    if p['source_id']=='S05':qual+='; out of stock'
    rows.append([name, '$'+format(float(p['unit_usd']),'.2f'),qual])
bottom=table(['Item','USD / unit','Evidence'],rows,[247,72,123],36,511)
y=para('$'+format(custom_total,'.2f'),510,505,240,27,True,ACCENT)
y=para('Planning total, including estimated assembly and simple packaging.',510,y-12,240,13,True)
y=para('Allow roughly $31-$38 with a small contingency. Freight, tariffs, tax, engineering, tooling, extended burn-in and returns are still outside this estimate.',510,y-19,240,13)
y=para('The controller reference is out of stock at DigiKey. Sourcing or substitution must be resolved before committing to a custom board.',510,y-19,240,10)
y=para('$45 retail',510,y-23,240,13,True)
y=para('At $31.01 build cost, $13.99 remains before payment fees, delivery, development and returns. That is about 31% gross margin at this stage.',510,y-12,240,10)
y=para('For comfortable $45 direct sales, target about $20-$22 landed. Reaching that requires a firmer enclosure quote, simpler assembly and a supplier cost-down round.',510,y-18,240,10)
para('The cited component subtotal is $19.21; the remaining $11.80 consists of unquoted planning allowances. A verified sub-$30 offer has not been found.',36,70,720,10)

page('Power sets the rules', 'All device loads below are engineering assumptions, not measurements. A two-color TFT still draws power for its backlight.')
y=para('Ordinary indoor light is far too little.',36,509,344,13,True)
y=para('An indoor-optimized solar cell can produce up to 22 microwatts/cm2 at 500 lux. Even a generous 100 cm2 face yields only 2.2 mW while lit. '+link_source('S11'),36,y-15,344,13)
y=para('With 12 hours of light, that is 0.0264 Wh/day before charging losses. A device averaging 0.6 W needs 14.4 Wh/day. The energy gap is about 545 times.',36,y-17,344,13)
y=para('This is an optimistic indoor-cell comparison. It is not a measured output claim for the outdoor Voltaic panel.',36,y-15,344,10)
para('Energy per day at a 0.6 W device load',414,509,342,13,True)
para('Continuous playback: 14.4 Wh',414,470,342,10)
c.setFillColor(GREEN);c.rect(414,437,326,13,fill=1,stroke=0)
para('Indoor solar example: 0.0264 Wh',414,416,342,10)
c.setFillColor(ACCENT);c.rect(414,386,max(.6,326*.0264/14.4),13,fill=1,stroke=0)
para('Bars share a linear scale. The second bar is smaller than one point.',414,372,342,10)
table(['Assumed average load','Daily energy','2200mAh cell runtime*'],[
    ['0.3 W, dim / muted','7.2 Wh','23 hours'],
    ['0.6 W, quiet audio','14.4 Wh','11.5 hours'],
    ['1.0 W, brighter / louder','24 Wh','6.9 hours']
],[139,78,125],414,327)
para('*Runtime assumes 3.7 V x 2.2 Ah x 85% usable energy / load. Cells age. '+link_source('S14'),414,210,342,10)
bottom=table(['Power option','What the object requires'],[
    ['USB-C / no battery','Best first version. Thin cable to an existing powered USB port; no battery replacement routine.'],
    ['Wired plinth / contacts','Moves the cable to the stand. The stand still plugs in; lifting the object stops playback.'],
    ['Solar + battery','P124 panel + charger + cell alone add $38.90 one-off, before boost and wiring. '+link_source('S12')+' '+link_source('S13')+' '+link_source('S14')]
],[170,550],36,177)
para('Desktop AC option: MEAN WELL 5 V supply, $14.10 plus AC lead and USB-C adapter. Optional extra. '+link_source('S15'),36,bottom-13,720,10)

page('Crude image. Considered sound.', 'An architecture proposal, not a demonstrated electronics build. The exploded rendering shows component envelopes rather than a designed assembly.')
imagefit(RENDERS/'07_exploded_envelope.png',36,205,349,306)
para('2.8-inch module: 73.06 x 50.54 x 10 mm envelope.<br/>40 mm speaker: 5 mm thick; separate chamber required.<br/>Optional 68 x 31 x 5 mm steel plate: about 83 g.',36,191,349,10)
para('A hand-weight target of roughly 180-250 g can be pursued with ballast after the actual assembly is weighed. No battery is necessary to create that feel.',36,126,349,10)
y=para('Keep the original motion and timing.',414,510,342,13,True)
y=para('Preconvert the chosen song to 160 x 120, two colors, at about 12 fps. Show each logical pixel as a 2 x 2 block on a 320 x 240 TFT. Approve the crop or letterbox per song.',414,y-13,342,13)
y=para('Separate picture austerity from audio quality: mono 44.1 kHz / 16-bit PCM can remain intact while the picture is aggressively dithered.',414,y-16,342,13)
y=para('Raw one-bit frames need 28,800 bytes/s at 12 fps. Mono PCM needs 88,200 bytes/s. A four-minute song totals about 28.1 MB before headers, so a 128MB card has ample room.',414,y-15,342,10)
y=para('Spend care on the acoustic enclosure.',414,y-20,342,13,True)
y=para('Audition the supplied speaker against the 8-ohm PUI round driver. Seal the front/back acoustic path with a gasket, isolate the chamber from loose parts, and compare level-matched recordings. '+link_source('S02')+' '+link_source('S07'),414,y-13,342,10)
y=para('A 400 Hz-resonance miniature driver will have limited deep bass. Prioritize clear voice and guitar at shelf-listening levels. Driver wattage is a limit, not a sound-quality rating. '+link_source('S18'),414,y-14,342,10)
y=para('Mute should silence the amplifier while video and timing continue. Set one comfortable factory volume; a single physical button is sufficient.',414,y-14,342,10)
para('Ordinary budget e-paper is unsuitable for this video loop: the cited 2.7-inch module takes about six seconds for a full refresh. A reflective memory LCD is a separate, pricier path, with video performance still to validate. '+link_source('S17')+' '+link_source('S10'),36,70,720,10)

for title, pair in [('Black objects',concepts[:2]),('Warm objects',concepts[2:4]),('Power becomes part of the form',concepts[4:])]:
    page(title)
    for i,a in enumerate(pair):
        x=36+i*372
        imagefit(RENDERS/a['file'],x,242,348,290)
        y=para(a['id']+' '+a['name'],x,232,348,13,True)
        y=para(' x '.join(map(str,a['dimensions']))+' mm | '+a['display'],x,y-8,348,10)
        y=para(a['description'],x,y-14,348,10)
        y=para('<b>Finish:</b> '+a['finish'],x,y-12,348,10)
        y=para('<b>Cost:</b> '+a['cost'],x,y-10,348,10)
        para('<b>To resolve:</b> '+a['risk'],x,y-10,348,10)

page('Build the smallest useful prototype')
imagefit(RENDERS/'08_shelf_context.png',36,247,426,277)
para('Monolith in a shelf context. Props provide scale; shelf and material finishes are illustrative.',36,233,426,10)
y=para('1. Prove the loop.',494,512,262,13,True)
y=para('Buy one board and one card. Load a real, approved song. Confirm power-up, picture/audio timing, mute behavior and a clean repeat. Disable Wi-Fi and Bluetooth during playback.',494,y-12,262,10)
y=para('2. Measure before promising solar.',494,y-21,262,13,True)
y=para('Measure USB input watts muted and audible at the intended brightness. Test the actual shelf and panel for a full day. Recalculate from those measurements.',494,y-12,262,10)
y=para('3. Compare sound inside the case.',494,y-21,262,13,True)
y=para('Try the supplied speaker and the 40 mm driver in gasketed test chambers. Listen at matched level. Check for buzz, rattle and heat over a continuous 72-hour run.',494,y-12,262,10)
y=para('4. Get one real batch quote.',494,y-21,262,13,True)
para('Request 100 and 500 unit prices covering electronics, programmed media, assembly, enclosure, QC, packaging and delivery. Resolve the controller stock issue and obtain a landed price before fixing retail.',494,y-12,262,10)
y=para('A practical first specification',36,188,426,13,True)
y=para('One fixed song stored locally; 160 x 120 two-color picture; continuous motion at about 12 fps; mono PCM audio; one mute button; 5 V USB power; no battery; fine matte black shell.',36,y-14,426,13)
para('The $45 version depends on simpler production and a firm batch quote. Solar and real wood can remain separate editions. Conductive contacts can move the visible cable to a stand.',36,75,720,10)

page('Sources and buying notes', 'Links below open the product or engineering page. Source notes distinguish live reads, indexed listings and estimates. No orders have been placed.')
for col in range(2):
    y=509
    for s in sources[col*9:(col+1)*9]:
        xx=36+col*372
        y=para(link_source(s['id'],s['id']+'  '+s['title']),xx,y,347,10,True)
        # Keep the catalogue compact; the complete notes remain in the CSV/JSON.
        note=s['note']
        if len(note)>110:note=note[:107].rsplit(' ',1)[0]+'.'
        y=para(escape(note),xx,y-4,347,10)-6
    assert y>42, ('Sources overflow',col,y)

c.save()
print('Created PDF and comparison image. Custom estimate:',round(custom_total,2))
