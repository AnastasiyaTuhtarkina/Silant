$(document).ready(function () {
  // Функция для переключения вкладок
  window.openTab = function (evt, tabName) {
    // Скрываем все вкладки
    $(".tab-content").hide();

    // Убираем активный класс у всех кнопок
    $(".tab-button").removeClass("active");

    // Показываем текущую вкладку и добавляем активный класс к кнопке
    $("#" + tabName).show();

    if (evt) {
      $(evt.currentTarget).addClass("active");
    } else {
      // Если функция вызвана без события (при загрузке)
      $(".tab-button[onclick*='" + tabName + "']").addClass("active");
    }

    // Перерисовываем таблицу при переключении вкладок
    if ($.fn.DataTable.isDataTable("#" + tabName + " .dataTable")) {
      $("#" + tabName + " .dataTable")
        .DataTable()
        .columns.adjust()
        .draw();
    }
  };

  // Проверяем якорь при загрузке
  var hash = window.location.hash;
  if (hash) {
    openTab(null, hash.substring(1));
  } else {
    // По умолчанию открываем первую вкладку
    openTab(null, "tab1");
  }

  // Инициализация DataTables с задержкой для корректного отображения
  setTimeout(function () {
    $(".dataTable").each(function () {
      if (!$.fn.DataTable.isDataTable(this)) {
        var table = $(this).DataTable({
          paging: true,
          searching: true,
          ordering: true,
          info: true,
          pageLength: 10,
          language: {
            url: languageUrl,
          },
          initComplete: function () {
            var columnsWithFilters = $(this)
              .data("filter-columns")
              .split(",")
              .map(Number);

            this.api()
              .columns(columnsWithFilters)
              .every(function () {
                var column = this;
                var header = $(column.header());
                var select = $(
                  '<select class="form-control"><option value="">Все</option></select>'
                )
                  .appendTo(header)
                  .on("change", function () {
                    var value = $(this).val();
                    column.search(value).draw();
                  });

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
          createdRow: function (row, data, dataIndex) {
            // Восстанавливаем обработчики событий после перерисовки таблицы
            $(row)
              .find(".clickable-description")
              .on("click", handleDescriptionClick);
            $(row).find(".clickable-row").on("click", handleRowClick);
          },
        });
      }
    });
  }, 100);

  // Обработчик для модального окна с описанием
  function handleDescriptionClick(event) {
    event.stopPropagation();
    const name = $(this).data("name");
    const description = $(this).data("description") || "Нет описания";

    if (name) {
      $("#modal-title").text(name);
      $("#modal-description").text(description);
      $("#modal").show();
    }
  }

  // Обработчик кликов по строкам таблицы
  function handleRowClick() {
    const machineId = $(this).closest("tr").data("id");
    if (machineId) {
      window.location.href = `/machine_detail/${machineId}/`;
    }
  }

  // Инициализация обработчиков событий
  $(document).on("click", ".clickable-description", handleDescriptionClick);
  $(document).on("click", ".clickable-row", handleRowClick);

  // Закрытие модального окна
  window.closeModal = function () {
    $("#modal").hide();
  };

  // Закрытие модального при клике вне его
  $(document).on("click", function (event) {
    if ($(event.target).is("#modal")) {
      $("#modal").hide();
    }
  });
});
