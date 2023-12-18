overworld_normal="https://www.spriters-resource.com/download/120364/"
overworld_rain="https://www.spriters-resource.com/download/120363/"
overworld_snow="https://www.spriters-resource.com/download/120362/"
overworld_units="https://www.spriters-resource.com/download/11827/"

custom_woods_normal="https://files.catbox.moe/d8m7hx.png"
custom_woods_rain="https://files.catbox.moe/9cwgwc.png"
custom_woods_snow="https://files.catbox.moe/ppck4v.png"

if [ ! -d './original_assets' ]; then
	mkdir -p './original_assets'
fi

curl $overworld_normal -o "./original_assets/overworld_normal.png"
curl $overworld_snow -o "./original_assets/overworld_snow.png"
curl $overworld_rain -o "./original_assets/overworld_rain.png"
curl $overworld_units -o "./original_assets/overworld_units.png"

curl $custom_woods_normal -o "./original_assets/custom_woods_normal.png"
curl $custom_woods_rain -o "./original_assets/custom_woods_rain.png"
curl $custom_woods_snow -o "./original_assets/custom_woods_snow.png"
