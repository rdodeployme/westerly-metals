/* =====================================================================
   WESTERLY METALS: TODAY'S RATES
   This is the only file to edit to update prices on the website.

   - Rates are dollars per kilo for clean, sorted metal. Example: 0.35
   - Handling fees are dollars per item. Example: 40
   - Leave a value as null to show "Call" (rates) or "Quoted" (fees).
   - Set "updated" to when the rates were last set.
   The price board and the load estimate on prices.html read from here.

   Current values (22 Oct 2026) are INDICATIVE starting rates, not the
   yard's own sheet: per-kg rates are the low end of a Melbourne yard's
   published list (Vicstar Metals, updated 17 Oct 2026), with grades it
   doesn't list scaled from other Melbourne lists. Fridge and air-con fees
   follow a regional council degassing fee (Strathbogie 2025-26, $28.50).
   Replace with Westerly's own rates before promoting the page.
   ===================================================================== */
window.WM_RATES = {
  updated: "22 Oct 2026, indicative",

  rates: {
    "cu-bright": 15.00, "cu-no2": 11.00, "cu-cable": 3.00, "cu-looms": 1.00,
    "cu-hws": 5.00, "cu-motors": 0.50, "cu-comp": 0.30, "cu-alt": 0.60,

    "al-ext": 2.00, "al-cast": 1.00, "al-sheet": 1.00, "al-wheels": 2.00,
    "al-rads": 1.20, "al-cans": 0.80, "al-engines": 0.70,

    "br-clean": 7.00, "br-irony": 4.50, "br-rads": 6.50,

    "st-heavy": 0.25, "st-light": 0.15, "st-cast": 0.20, "st-mixed": 0.10,
    "st-cars": 0.15, "st-part": 0.05,

    "ss-304": 1.20, "ss-316": 1.80, "ss-irony": 0.80,

    "pb-soft": 1.00, "pb-weights": 0.90, "pb-batt": 0.30
  },

  fees: {
    "fee-fridge": 30, "fee-aircon": 30
  }
};
