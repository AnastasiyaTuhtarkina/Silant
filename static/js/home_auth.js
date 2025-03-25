$(document).ready(function () {
  var table = $("#machineTable").DataTable({
    paging: true,
    searching: true,
    ordering: true,
    info: true,
    pageLength: 10,
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/ru.json",
    },
    initComplete: function () {
      // Указываем индексы столбцов, которые должны иметь фильтры
      var columnsWithFilters = [1, 3, 5, 7, 9]; // Индексы столбцов (начиная с 0)

      // Добавляем выпадающие списки только для указанных столбцов
      this.api()
        .columns(columnsWithFilters)
        .every(function () {
          var column = this;
          var header = $(column.header());
          var select = $('<select><option value="">Все</option></select>')
            .appendTo(header) // Добавляем в заголовок столбца
            .on("change", function () {
              var value = $(this).val();
              column.search(value).draw(); // Применяем фильтр
            });

          // Заполняем выпадающий список уникальными значениями из столбца
          column
            .data()
            .unique()
            .sort()
            .each(function (value) {
              select.append(
                '<option value="' + value + '">' + value + "</option>"
              );
            });
        });
    },
  });
});

// Функция для переключения вкладок
function openTab(evt, tabName) {
  // Скрываем все вкладки
  var tabs = document.getElementsByClassName("tab");
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].style.display = "none";
  }

  // Убираем активный класс у всех кнопок
  var buttons = document.getElementsByClassName("tab-button");
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].classList.remove("active");
  }

  // Показываем текущую вкладку и добавляем активный класс к кнопке
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.classList.add("active");
}

// При загрузке страницы показываем первую вкладку
window.onload = function () {
  document.getElementById("tab1").style.display = "block"; // Показываем первую вкладку
  document.querySelector(".tab-button").classList.add("active"); // Делаем первую кнопку активной
};
