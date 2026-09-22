from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kemisetso's Save More - Fresh Eggs & Flash Deals</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --primary-yellow: #FFC107;
            --accent-green: #2E7D32;
            --accent-blue: #0288D1;
            --dark-blue: #1A237E;
            --bg-cream: #F8F9FA;
            --card-bg: #FFFFFF;
            --text-dark: #2B2B2B;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }
        body { background-color: var(--bg-cream); color: var(--text-dark); line-height: 1.5; padding-bottom: 40px; }

        header {
            background: linear-gradient(135deg, #1A237E 0%, #0288D1 100%);
            color: white; text-align: center; padding: 35px 15px;
            border-bottom-left-radius: 25px; border-bottom-right-radius: 25px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }

        .badge {
            background: var(--primary-yellow); color: #000; padding: 5px 14px;
            font-weight: 700; border-radius: 20px; font-size: 0.8rem;
            text-transform: uppercase; letter-spacing: 1px; display: inline-block; margin-bottom: 10px;
        }

        header h1 { font-size: 1.8rem; font-weight: 800; }
        header p { font-size: 1rem; opacity: 0.95; }
        .contact-header { font-weight: 700; color: var(--primary-yellow); margin-top: 5px; }

        .container { max-width: 850px; margin: 0 auto; padding: 15px; }

        .promo-card {
            background: #E8F5E9; border: 2px dashed var(--accent-green);
            border-radius: 14px; padding: 14px; text-align: center; margin: 15px 0;
        }
        .promo-card h3 { color: var(--accent-green); font-size: 1.1rem; }

        /* Product Cards */
        .product-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px; margin-bottom: 20px;
        }

        .product-card {
            background: var(--card-bg); border-radius: 16px; padding: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06); border: 1px solid #E0E0E0;
            display: flex; flex-direction: column; justify-content: space-between;
        }

        .product-img {
            width: 100%; height: 160px; object-fit: cover; border-radius: 12px; margin-bottom: 12px;
        }

        .product-card h2 { font-size: 1.2rem; font-weight: 700; color: var(--dark-blue); margin-bottom: 5px; }
        .product-card p { font-size: 0.85rem; color: #555; margin-bottom: 12px; }

        .input-group { margin-top: 10px; }
        .input-group label { display: block; font-weight: 600; font-size: 0.85rem; margin-bottom: 5px; }
        .input-group input, .input-group select, .input-group textarea {
            width: 100%; padding: 10px; border: 1px solid #CCC; border-radius: 8px; font-size: 0.95rem;
        }

        /* Form Sections */
        .section-box {
            background: var(--card-bg); border-radius: 16px; padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06); border: 1px solid #E0E0E0; margin-bottom: 20px;
        }

        .section-box h3 { font-size: 1.1rem; color: var(--dark-blue); margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }

        /* Star Rating Style */
        .star-rating {
            display: flex; gap: 8px; font-size: 1.8rem; color: #CCC; cursor: pointer; margin-bottom: 12px;
        }
        .star-rating i.active {
            color: var(--primary-yellow);
        }

        /* Summary & Checkout */
        .summary-box {
            background: var(--dark-blue); color: white; padding: 20px; border-radius: 18px;
            box-shadow: 0 8px 25px rgba(26, 35, 126, 0.25);
        }

        .summary-box h2 { font-size: 1.3rem; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 8px; }
        .summary-line { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.95rem; }
        .summary-line.total { font-size: 1.25rem; font-weight: 800; color: var(--primary-yellow); border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px; }

        .btn-order {
            width: 100%; background: #25D366; color: white; border: none; padding: 15px;
            border-radius: 12px; font-size: 1.1rem; font-weight: 700; cursor: pointer;
            margin-top: 15px; display: flex; align-items: center; justify-content: center; gap: 10px;
            transition: background 0.2s ease;
        }
        .btn-order:hover { background: #1EBE5D; }

        .btn-feedback {
            width: 100%; background: var(--accent-blue); color: white; border: none; padding: 12px;
            border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer;
            margin-top: 10px; display: flex; align-items: center; justify-content: center; gap: 8px;
        }

        .note { font-size: 0.8rem; color: #666; text-align: center; margin-top: 12px; }
    </style>
</head>
<body>

    <header>
        <span class="badge"><i class="fa-solid fa-truck-fast"></i> Express Local Delivery</span>
        <h1>KEMISETSO'S SAVE MORE</h1>
        <p>Fresh Eggs, Flash Deals & Local Essentials Direct To You!</p>
        <div class="contact-header">
            <i class="fa-solid fa-phone"></i> Call / WhatsApp: 0659747297
        </div>
    </header>

    <div class="container">
        
        <div class="promo-card">
            <h3><i class="fa-solid fa-gift"></i> FREE DELIVERY SPECIAL!</h3>
            <p>Order <strong>4 or more Egg Trays (30s)</strong> and get <strong>FREE DELIVERY!</strong> 🎉</p>
        </div>

        <form id="storeForm">
            <!-- Products Grid -->
            <div class="product-grid">
                
                <!-- 1. Fresh Eggs -->
                <div class="product-card">
                    <div>
                        <img src="https://images.unsplash.com/photo-1582721478779-0ae163c05a60?auto=format&fit=crop&w=500&q=80" alt="Fresh Egg Tray" class="product-img">
                        <h2>Fresh Farm Eggs</h2>
                        <p>High quality, nutritious local farm eggs. <strong>R55 per tray (30 Eggs)</strong>.</p>
                    </div>
                    <div class="input-group">
                        <label for="eggTrays">Select Trays (30s):</label>
                        <input type="number" id="eggTrays" value="0" min="0" onchange="calculateTotal()">
                    </div>
                </div>

                <!-- 2. Airtime -->
                <div class="product-card">
                    <div>
                        <img src="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=500&q=80" alt="Airtime" class="product-img">
                        <h2>Airtime Top-Up</h2>
                        <p>Vodacom, MTN, Telkom & Cell C instant airtime top-ups.</p>
                    </div>
                    <div class="input-group">
                        <label for="airtimeNetwork">Network & Amount:</label>
                        <select id="airtimeNetwork" onchange="calculateTotal()">
                            <option value="0">None</option>
                            <option value="10">R10 Airtime</option>
                            <option value="20">R20 Airtime</option>
                            <option value="50">R50 Airtime</option>
                            <option value="100">R100 Airtime</option>
                        </select>
                    </div>
                </div>

                <!-- 3. Flash Deals & Offers -->
                <div class="product-card">
                    <div>
                        <img src="https://images.unsplash.com/photo-1556742049-0a67daf40955?auto=format&fit=crop&w=500&q=80" alt="Electricity & Services" class="product-img">
                        <h2>Flash Deals & Offers</h2>
                        <p>Pay Electricity Tokens, DSTV, or special voucher offers.</p>
                    </div>
                    <div class="input-group">
                        <label for="flashService">Service Type:</label>
                        <select id="flashService">
                            <option value="None">None</option>
                            <option value="Prepaid Electricity">Prepaid Electricity</option>
                            <option value="DSTV / PayTV">DSTV / PayTV</option>
                            <option value="Data Bundle Offer">Data Bundle Deal</option>
                        </select>
                    </div>
                    <div class="input-group" style="margin-top: 8px;">
                        <label for="flashAmount">Amount / Value (R):</label>
                        <input type="number" id="flashAmount" value="0" min="0" step="10" onchange="calculateTotal()">
                    </div>
                </div>

            </div>

            <!-- Location Details -->
            <div class="section-box">
                <h3><i class="fa-solid fa-location-dot" style="color: red;"></i> Step 2: Choose Your Delivery Location</h3>
                <div class="input-group">
                    <label for="locationArea">Select Your Area in/around Mmakau:</label>
                    <select id="locationArea" onchange="calculateTotal()">
                        <option value="15|Mmakau Central">Mmakau Central (R15 Delivery)</option>
                        <option value="20|Mmakau Section 2">Mmakau Section 2 (R20 Delivery)</option>
                        <option value="25|Mmakau Extension">Mmakau Extension / Outskirts (R25 Delivery)</option>
                        <option value="30|Surrounding Area">Surrounding Area (R30 Delivery)</option>
                    </select>
                </div>
                <div class="input-group" style="margin-top: 10px;">
                    <label for="streetAddress">Exact Street Name / House Number / Landmark:</label>
                    <input type="text" id="streetAddress" placeholder="e.g. Near Mmakau Primary School, House 123">
                </div>
            </div>

            <!-- Payment Method -->
            <div class="section-box">
                <h3><i class="fa-solid fa-wallet" style="color: var(--accent-green);"></i> Step 3: Choose Payment Method</h3>
                <div class="input-group">
                    <select id="paymentMethod" onchange="togglePaymentNotice()">
                        <option value="Cash on Delivery">Cash on Delivery</option>
                        <option value="Card (Swipe on Delivery)">Card (Swipe on Delivery)</option>
                        <option value="Online Payment (WhatsApp Transfer)">Online Payment / EFT (via WhatsApp)</option>
                    </select>
                </div>
                <p id="paymentNotice" style="font-size: 0.85rem; color: #D32F2F; margin-top: 8px; display: none;">
                    <strong>Note:</strong> Online payments are safely processed via WhatsApp confirmation.
                </p>
            </div>

            <!-- Summary Box -->
            <div class="summary-box">
                <h2>Order Summary</h2>
                <div class="summary-line">
                    <span>Egg Trays Subtotal:</span>
                    <span id="eggSubtotal">R0.00</span>
                </div>
                <div class="summary-line">
                    <span>Airtime Subtotal:</span>
                    <span id="airtimeSubtotal">R0.00</span>
                </div>
                <div class="summary-line">
                    <span>Flash Deals / Services:</span>
                    <span id="flashSubtotal">R0.00</span>
                </div>
                <div class="summary-line">
                    <span>Delivery Fee:</span>
                    <span id="deliveryFee">R15.00</span>
                </div>
                <div class="summary-line total">
                    <span>Grand Total:</span>
                    <span id="grandTotal">R15.00</span>
                </div>

                <button type="button" class="btn-order" onclick="submitWhatsAppOrder()">
                    <i class="fa-brands fa-whatsapp"></i> Order Preferable via WhatsApp
                </button>
            </div>
        </form>

        <!-- Customer Rating & Feedback Section -->
        <div class="section-box" style="margin-top: 25px;">
            <h3><i class="fa-solid fa-star" style="color: var(--primary-yellow);"></i> Rate Our Service & Leave Feedback</h3>
            <p style="font-size: 0.85rem; color: #555; margin-bottom: 10px;">How was your experience ordering with us?</p>
            
            <div class="star-rating" id="starContainer">
                <i class="fa-solid fa-star" onclick="setRating(1)"></i>
                <i class="fa-solid fa-star" onclick="setRating(2)"></i>
                <i class="fa-solid fa-star" onclick="setRating(3)"></i>
                <i class="fa-solid fa-star" onclick="setRating(4)"></i>
                <i class="fa-solid fa-star" onclick="setRating(5)"></i>
            </div>

            <div class="input-group">
                <label for="feedbackText">Your Comments or Suggestions:</label>
                <textarea id="feedbackText" rows="3" placeholder="Tell us how we can serve you better..."></textarea>
            </div>

            <button type="button" class="btn-feedback" onclick="sendFeedbackWhatsApp()">
                <i class="fa-solid fa-comment-dots"></i> Submit Review & Feedback
            </button>
        </div>

        <p class="note">Prefer to order directly by phone? Call or SMS us anytime at <strong>0659747297</strong>!</p>
    </div>

    <script>
        let selectedStars = 0;

        function setRating(stars) {
            selectedStars = stars;
            let starIcons = document.querySelectorAll('#starContainer i');
            starIcons.forEach((star, index) => {
                if (index < stars) {
                    star.classList.add('active');
                } else {
                    star.classList.remove('active');
                }
            });
        }

        function calculateTotal() {
            let eggTrays = parseInt(document.getElementById('eggTrays').value) || 0;
            let airtimeVal = parseFloat(document.getElementById('airtimeNetwork').value) || 0;
            let flashVal = parseFloat(document.getElementById('flashAmount').value) || 0;

            let locationData = document.getElementById('locationArea').value.split('|');
            let deliveryBase = parseFloat(locationData[0]);

            let eggCost = eggTrays * 55;
            let deliveryCost = deliveryBase;

            // Free delivery if 4 or more egg trays
            if (eggTrays >= 4) {
                deliveryCost = 0;
            } else if (eggTrays === 0 && (airtimeVal > 0 || flashVal > 0)) {
                deliveryCost = 5; // Flat reduced delivery for virtual services
            } else if (eggTrays === 0 && airtimeVal === 0 && flashVal === 0) {
                deliveryCost = 0;
            }

            let grandTotal = eggCost + airtimeVal + flashVal + deliveryCost;

            document.getElementById('eggSubtotal').innerText = 'R' + eggCost.toFixed(2);
            document.getElementById('airtimeSubtotal').innerText = 'R' + airtimeVal.toFixed(2);
            document.getElementById('flashSubtotal').innerText = 'R' + flashVal.toFixed(2);
            document.getElementById('deliveryFee').innerText = (deliveryCost === 0 && (eggTrays > 0 || airtimeVal > 0 || flashVal > 0)) ? 'FREE 🎉' : 'R' + deliveryCost.toFixed(2);
            document.getElementById('grandTotal').innerText = 'R' + grandTotal.toFixed(2);
        }

        function togglePaymentNotice() {
            let method = document.getElementById('paymentMethod').value;
            let notice = document.getElementById('paymentNotice');
            if (method.includes('Online Payment')) {
                notice.style.display = 'block';
            } else {
                notice.style.display = 'none';
            }
        }

        function submitWhatsAppOrder() {
            let eggTrays = parseInt(document.getElementById('eggTrays').value) || 0;
            let airtimeVal = parseFloat(document.getElementById('airtimeNetwork').value) || 0;
            let flashService = document.getElementById('flashService').value;
            let flashVal = parseFloat(document.getElementById('flashAmount').value) || 0;

            if (eggTrays === 0 && airtimeVal === 0 && flashVal === 0) {
                alert('Please select at least 1 item to place an order.');
                return;
            }

            let locationArea = document.getElementById('locationArea').value.split('|')[1];
            let streetAddress = document.getElementById('streetAddress').value.trim();

            if (!streetAddress) {
                alert('Please enter your street address or landmark so we know where to deliver!');
                return;
            }

            let paymentMethod = document.getElementById('paymentMethod').value;
            let total = document.getElementById('grandTotal').innerText;
            let myPhoneNumber = "27659747297"; // WhatsApp Number

            // Build items summary using template literals
            let itemsList = "";
            if (eggTrays > 0) itemsList += `• Fresh Farm Eggs: ${eggTrays} Tray(s) (30s)\n`;
            if (airtimeVal > 0) itemsList += `• Airtime: R${airtimeVal}\n`;
            if (flashVal > 0) itemsList += `• Flash Deal (${flashService}): R${flashVal}\n`;

            let rawMessage = `🛒 *KEMISETSO'S SAVE MORE - NEW ORDER*
═══════════════════

*ITEMS ORDERED:*
${itemsList}
📍 *DELIVERY LOCATION:*
• Area: ${locationArea}
• Address/Landmark: ${streetAddress}

💳 *PAYMENT METHOD:* ${paymentMethod}
💰 *TOTAL AMOUNT:* ${total}

═══════════════════
Please confirm and process my order!`;

            let encodedMessage = encodeURIComponent(rawMessage);
            window.open(`https://wa.me/${myPhoneNumber}?text=${encodedMessage}`, '_blank');
        }

        function sendFeedbackWhatsApp() {
            let comment = document.getElementById('feedbackText').value.trim();
            
            if (selectedStars === 0 && !comment) {
                alert('Please select a star rating or type a comment before submitting.');
                return;
            }

            let feedbackPhoneNumber = "27698907756"; 

            let feedbackMsg = `⭐ *CUSTOMER FEEDBACK - KEMISETSO'S SAVE MORE*
═══════════════════

*Rating:* ${selectedStars ? selectedStars + "/5 Stars" : "Not rated"}
*Comments:* ${comment ? comment : "No comment provided."}

═══════════════════
Thank you for helping us improve our service!`;

            let encodedFeedback = encodeURIComponent(feedbackMsg);
            window.open(`https://wa.me/${feedbackPhoneNumber}?text=${encodedFeedback}`, '_blank');
        }

        // Initialize calculation
        calculateTotal();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
