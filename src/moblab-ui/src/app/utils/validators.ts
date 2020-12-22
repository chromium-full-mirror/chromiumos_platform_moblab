export function forbiddenIDValidator(control) {
  if (!control.value) {
    return null;
  }
  const forbidden = !new RegExp('^\\d+$').test(control.value);
  return forbidden ? {notANonnegativeNumber: {value: control.value}} : null;
}

export function forbiddenDateValidator(control) {
  if (!control.value) {
    return null;
  }
  const timestamp = new Date(control.value).getTime();
  if (isNaN(timestamp)) {
    return {failedDateParse: {value: control.value}};
  }
  if (timestamp <= 0) {
    return {dateOutOfBounds: {value: control.value}};
  }
  return null;
}

export function numericValidator(control) {
  if (!control.value) {
    return null;
  }

  if (isNaN(control.value)) {
    return {isNaN: {value: control.value}};
  }
  return null;
}

export function leadingTrailingWhitespaceValidator(control) {
  if (control.value.length !== control.value.trim().length) {
    return {leadingTrailingwhitespace: true};
  } else {
    return null;
  }
}
