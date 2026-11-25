(() => {
  const sample = document.querySelector("#sample");
  const family = document.querySelector("#family");
  const style = document.querySelector("#style");
  const size = document.querySelector("#size");
  const sizeValue = document.querySelector("#size-value");
  const reset = document.querySelector("#reset");
  const phrases = {
    mono: sample.defaultValue,
    sans: "A place for everything.\nAn interface for the everyday.",
    serif: "A mark on the page,\na pause between lines.",
  };
  let edited = false;

  function setFace() {
    const familyName = family.selectedOptions[0].textContent;
    sample.style.fontFamily = 'var(--' + family.value + ')';
    sample.style.fontWeight = style.selectedOptions[0].dataset.weight;
    sample.style.fontStyle = style.selectedOptions[0].dataset.slant;
    document.querySelector("#proof-name").textContent = familyName + " / " + style.selectedOptions[0].textContent;
  }

  family.addEventListener("change", () => {
    if (!edited) sample.value = phrases[family.value];
    setFace();
  });
  style.addEventListener("change", setFace);
  size.addEventListener("input", () => {
    sample.style.fontSize = size.value + "px";
    sizeValue.value = size.value + " px";
    size.setAttribute("aria-valuetext", size.value + " pixels");
  });
  sample.addEventListener("input", () => { edited = true; });
  reset.addEventListener("click", () => {
    sample.value = phrases[family.value];
    edited = false;
    sample.focus();
  });
  document.querySelector(".settings").hidden = false;
  reset.hidden = false;
})();
