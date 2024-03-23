/*-------------------Fuel Quote Update-------------------*/
const fuelGallons = document.getElementById("gallons");
const gallonsError = document.getElementById("gallonsError");
const delivery_dateInput = document.getElementById("delivery_date");
const costDisplay = document.getElementById("cost-shown");

function validateForm() {
  gallonsError.style.display = "none";
  if (isNaN(parseFloat(fuelGallons.value)) || !isFinite(fuelGallons.value)) {
    gallonsError.style.display = "inline";
    return false;
  }
  gallonsError.style.display = "none";

  return true;
}

function updateFuelQuote() {
  const gallons = parseFloat(fuelGallons.value);
  const delivery_date = delivery_dateInput.value;

  //delivery fee
  const deliveryFee = 1.75;

  //base price calulation
  const pricePerGallon = 3.05;
  const basePrice = pricePerGallon * gallons;
  const estimatedCost = basePrice;
  console.log(basePrice);
  //tax fee
  const taxRate = 0.0775;
  const taxFee = basePrice * taxRate;

  //total price
  const totalPrice = deliveryFee + taxFee + basePrice;

  //update display
  costDisplay.innerHTML = `${estimatedCost.toFixed(2)}`;
  document.getElementById("price-shown").innerHTML = `${pricePerGallon.toFixed(
    2
  )}`;
  document.getElementById("delivery-shown").innerHTML = `${deliveryFee.toFixed(
    2
  )}`;
  document.getElementById("total").innerHTML = `${totalPrice.toFixed(2)}`;
  document.getElementById("tax-shown").innerHTML = `${taxFee.toFixed(2)}`;
  document.getElementById("gallons-shown").innerHTML = `${gallons.toFixed(2)}`;
}

fuelGallons.addEventListener("input", validateForm);
fuelGallons.addEventListener("input", updateFuelQuote);
delivery_dateInput.addEventListener("input", updateFuelQuote);

/*----------Button Submit----------*/
const button = document.getElementById("button");
// button.addEventListener("click", function() {
//   if(validateForm()) {
//     updateFuelQuote();
//   }
// });

function cardSubmit() {}

// button.addEventListener("click", cardSubmit);

/*-------------------Fuel Quote Update-------------------*/
