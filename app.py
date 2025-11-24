from flask import Flask, request, send_file, send_from_directory
import re, io, urllib.parse, os

app = Flask(__name__)

CAREER_TEMPLATE = "https://www.linkedin.com/premium/redeem-v3/?_ed=COUPON&planType=career&redeemType=REFERRAL_COUPON&upsellOrderOrigin=premium_referrals_homepage_identity_1_sided_entry"
BUSINESS_TEMPLATE = "https://www.linkedin.com/premium/redeem-v3/?_ed=COUPON&planType=professional&redeemType=REFERRAL_COUPON&upsellOrderOrigin=premium_referrals_homepage_identity_1_sided_entry"

def extract_coupon(link):
    if "session_redirect=" in link:
        encoded = re.search(r"session_redirect=([^&]+)", link)
        if encoded:
            link = urllib.parse.unquote(encoded.group(1))
    match = re.search(r"coupon=([^&]+)", link)
    return match.group(1).strip() if match else None

def convert_link(link, mode):
    coupon = extract_coupon(link)
    if not coupon:
        return f"ERROR: No coupon found → {link}"
    template = CAREER_TEMPLATE if mode == "career" else BUSINESS_TEMPLATE
    return template.replace("COUPON", coupon, 1)

@app.route("/")
def homepage():
    return send_from_directory(".", "index.html")

@app.route("/convert", methods=["POST"])
def convert():
    mode = request.form.get("mode", "career")
    input_text = request.form.get("links", "")

    links = re.split(r"\s+", input_text.strip())
    output = [convert_link(link, mode) for link in links if link.strip()]

    if "download" in request.form:
        data = "\n".join(output)
        mem = io.BytesIO(data.encode())
        mem.seek(0)
        return send_file(mem, as_attachment=True, download_name="converted_links.txt")

    return "\n".join(output)

if __name__ == "__main__":
    app.run()
