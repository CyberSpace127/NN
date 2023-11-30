function searchTable() {
    let input, filter, table, tr, td, i;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    table = document.querySelector(".table");
    tr = table.getElementsByTagName("tr");

    for (i = 1; i < tr.length; i++) { // Start from 1 to skip the header row
      let visible = false; // Whether the row should be visible

      // Loop through all cells in the row
      td = tr[i].getElementsByTagName("td");
      for (let j = 0; j < td.length; j++) {
        if (td[j] && td[j].classList.contains("searchable")) {
          if (td[j].textContent.toUpperCase().indexOf(filter) > -1) {
            visible = true;
            break; // No need to check other cells in the same row
          }
        }
      }

      // Show or hide the row based on visibility
      if (visible) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }