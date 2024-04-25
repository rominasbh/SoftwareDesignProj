/*-------------------Fuel Quote Update-------------------*/
const fuelGallons = document.getElementById("gallons");
const gallonsError = document.getElementById("gallonsError");
const delivery_dateInput = document.getElementById("delivery_date");
const costDisplay = document.getElementById("cost-shown");
const userName = document.getElementById("client-name");
const price = document.getElementById("price-shown");
const delivery = document.getElementById("delivery-shown");
const total = document.getElementById("total");
const tax = document.getElementById("tax-shown");
const shownGallons = document.getElementById("gallons-shown");


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
  const gallon_value = fuelGallons.value.trim();
  const deliveryDateValue = delivery_dateInput.value.trim();
  console.log("the date in update: " + deliveryDateValue);


  if (
    gallon_value != "" &&
    parseFloat(gallon_value) > 0 &&
    deliveryDateValue != ""
  ) {
    const gallons = parseFloat(gallon_value);
    const delivery_date = deliveryDateValue;

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
    price.innerHTML = `${pricePerGallon.toFixed(2)}`;
    delivery.innerHTML = `${deliveryFee.toFixed(2)}`;
    total.innerHTML = `${totalPrice.toFixed(2)}`;
    tax.innerHTML = `${taxFee.toFixed(2)}`;
    shownGallons.innerHTML = `${gallons.toFixed(2)}`;
  } else {
    costDisplay.innerHTML = "--";
    price.innerHTML = "--";
    delivery.innerHTML = "--";
    total.innerHTML = "--";
    tax.innerHTML = "--";
    shownGallons.innerHTML = "--";
  }

  //debugging log: updated values
  console.log("Estimate: " + costDisplay.innerHTML);
  console.log("Delivery: " + delivery.innerHTML);
  console.log("Gallons: " + shownGallons.innerHTML);
  console.log("Total: " + total.innerHTML);
  console.log("Tax: " + tax.innerHTML);
  console.log("Price: " + price.innerHTML);
}

/*----------Set Date----------*/
function validateDate() {
  const curr_day = new Date();
  const adjustedDay = new Date(
    curr_day.getFullYear(),
    curr_day.getMonth(),
    curr_day.getDate(),
    0,
    0,
    0,
    0
  );

  const selectedDate = new Date(
    document.getElementById("delivery_date").value + "T00:00:00"
  );
  // selectedDate.setHours(0, 0, 0, 0);
  // const dateString = document.getElementById("delivery_date").value;
  // const [year, month, day] = dateString.split("-");
  // const selectedDate = new Date(Date.UTC(year, month - 1, day));
  // const selectedDate = new Date(document.getElementById("delivery_date").value);
  // selectedDate.setHours(0, 0, 0, 0);

  // console.log("Current Date: " + curr_day.toLocaleDateString());
  // console.log("Adjusted Date: " + adjustedDay.toLocaleDateString());
  console.log("Selected Date: " + selectedDate.toLocaleDateString());
  console.log("the del input var: " + delivery_dateInput.value);

  if (selectedDate <= adjustedDay) {
    console.log("Error Date: " + selectedDate.toLocaleDateString());
    console.log("Adjusted Date: " + adjustedDay.toLocaleDateString());
    console.log("Current Date: " + curr_day.toLocaleDateString());
    document.getElementById("date_error").style.display = "inline";
    return false;
  }

  document.getElementById("date_error").style.display = "none";
  return true;
}

function dateSelection() {
  const day = new Date();
  const dd = String(day.getDate()).padStart(2, "0");
  const mm = String(day.getMonth() + 1).padStart(2, "0");
  const yyyy = day.getFullYear();
  const today = mm + "-" + dd + "-" + yyyy;
  document.getElementById("delivery_date").min = today;

  const isValidDate = validateDate();
  if (isValidDate) {
    updateFuelQuote();
  }
}

function gallonDateValidation() {
  const isValidDate = validateDate();
  if (isValidDate) {
    updateFuelQuote();
  }
  console.log(isValidDate);
}

fuelGallons.addEventListener("input", gallonDateValidation);
delivery_dateInput.addEventListener("input", gallonDateValidation);

const confirmBtn = document.getElementById("confirm-quote");
const yesBtn = document.getElementById("yes_btn");
const noBtn = document.getElementById("no_btn");
const vqhBtn = document.getElementById("view_quote_history");
const newQuoteBtn = document.getElementById("new_quote");

// confirmBtn.addEventListener("click", () => {
//   document.getElementById("confirm_popup").style.display = "block";
// });
// confirmBtn.addEventListener("click", updateFuelQuote);

confirmBtn.addEventListener("click", () => {
  const gallonsInput = document.getElementById("gallons").value.trim();
  const deliveryDateInput = document
    .getElementById("delivery_date")
    .value.trim();
  if (gallonsInput !== "" && deliveryDateInput !== "") {
    document.getElementById("confirm_popup").style.display = "block";
    updateFuelQuote(); // Call the updateFuelQuote function only if inputs are valid
  } else {
    alert("Please enter values for gallons and delivery date.");
  }
});

yesBtn.addEventListener("click", () => {
  document.getElementById("confirm_popup").style.display = "none";
  document.getElementById("saved_quote").style.display = "block";

  const gal = parseFloat(fuelGallons.value.trim());
  const dDate = delivery_dateInput.value.trim();
  console.log("the del input @ yes: " + dDate);
  const totPrice = parseFloat(total.textContent.trim());

  const data = {
    gallons: gal,
    delivery_date: dDate,
    total_price: totPrice,
  };

  const xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        console.log("Quote saved successfully");
      } else {
        console.log("Error saving quote", xhr.statusText);
      }
    }
  };

  xhr.open("POST", "/fuel_quote", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(JSON.stringify(data));
});

noBtn.addEventListener("click", () => {
  document.getElementById("confirm_popup").style.display = "none";
  document.getElementById("saved_quote").style.display = "none";
});

vqhBtn.addEventListener("click", () => {
  location = "/fuel_history";
});

newQuoteBtn.addEventListener("click", () => {
  location = "/fuel_quote";
});

//making it interactive? once the desired price w desired date is found, click get quote to save the quote
// fuelGallons.addEventListener("input", validateForm);
// fuelGallons.addEventListener("input", updateFuelQuote);
// delivery_dateInput.addEventListener("input", updateFuelQuote);
// delivery_dateInput.addEventListener("input", dateSelection);

// this function makes sure that both date and gallon are filled in before displaying the quote and its
//interactive, changing the gallon changes the price and we might need to implement changing the date
//also change the price.
// function validateAndUpdateQuote() {
//   const deliveryDateValue = delivery_dateInput.value.trim();

//   const isValidGallons = validateForm();
//   //may want to check if the date is in right format but may not need too cuz we use calander
//   const isValidDeliveryDate = deliveryDateValue !== "";

//   if (isValidGallons && isValidDeliveryDate) {
//     updateFuelQuote();
//   }
// }

// // Attach validateAndUpdateQuote to the input event listeners
// fuelGallons.addEventListener("input", validateAndUpdateQuote);
// delivery_dateInput.addEventListener("input", validateAndUpdateQuote);

/*----------Button Submit----------*/
// const button = document.getElementById("button");
// // may have to fix this logic
// button.addEventListener("click", function () {
//   if (validateForm()) {
//     updateFuelQuote();
//   }
// });

// function cardSubmit() {}

// button.addEventListener("click", cardSubmit);

/*-------------------Fuel Quote Update-------------------*/
