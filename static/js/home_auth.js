$(document).ready(function () {
  var table = $("#machineTable").DataTable({
    paging: true,
    searching: true,
    ordering: true,
    info: true,
    pageLength: 10,
    language: {
      url: languageUrl, // Используем переменную, переданную из шаблона
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

$(document).ready(function () {
  // Обработчик кликов по ячейкам, которые открывают модальное окно
  $(".clickable-description").on("click", function (event) {
    event.stopPropagation(); // Остановить дальнейшую обработку события
    const name = $(this).data("name");
    const description = $(this).data("description") || "Нет описания"; // Установить значение по умолчанию

    if (name) {
      // Проверяем, что имя существует
      $("#modal-title").text(name);
      $("#modal-description").text(description); // Показываем описание, даже если оно пустое
      $("#modal").show(); // Показать модальное окно
    } else {
      console.warn("Отсутствует имя для отображения в модальном окне.");
    }
  });

  // Обработчик кликов по номеру строки (для перенаправления)
  $(".clickable-row").on("click", function () {
    const machineId = $(this).closest("tr").data("id"); // Получаем уникальный идентификатор машины
    console.log(machineId); // Проверяем, что идентификатор извлекается правильно
    window.location.href = `/machine_detail/${machineId}/`; // Перенаправляем на страницу деталей
  });
});

function closeModal() {
  $("#modal").hide(); // Скрыть модальное окно
}
