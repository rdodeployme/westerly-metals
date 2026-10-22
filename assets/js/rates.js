/* =====================================================================
   WESTERLY METALS: TODAY'S RATES
   This is the only file to edit to update prices on the website.

   - Rates are dollars per kilo for clean, sorted metal. Example: 0.35
   - Handling fees are dollars per item. Example: 40
   - Leave a value as null to show "Call" (rates) or "Quoted" (fees).
   - Set "updated" to when the rates were last set, e.g. "22 Oct 2026, 7am".
   The price board and the load estimate on prices.html read from here.
   ===================================================================== */
window.WM_RATES = {
  updated: "",

  rates: {
    "cu-bright": null, "cu-no2": null, "cu-cable": null, "cu-looms": null,
    "cu-hws": null, "cu-motors": null, "cu-comp": null, "cu-alt": null,

    "al-ext": null, "al-cast": null, "al-sheet": null, "al-wheels": null,
    "al-rads": null, "al-cans": null, "al-engines": null,

    "br-clean": null, "br-irony": null, "br-rads": null,

    "st-heavy": null, "st-light": null, "st-cast": null, "st-mixed": null,

    "ss-304": null, "ss-316": null, "ss-irony": null,

    "pb-soft": null, "pb-weights": null, "pb-batt": null
  },

  fees: {
    "fee-fridge": null, "fee-aircon": null, "fee-car": null,
    "fee-mixed": null
  }
};
