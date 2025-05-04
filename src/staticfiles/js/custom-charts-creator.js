const global_demography_category = (JSONSting) => {
  const ctx = document.getElementById("global_demography_category");
  const data = JSON.parse(
    JSONSting
  );
  const categories = Object.keys(data);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: categories,
      datasets: [
        {
          label: "Total Benefeciaries",
          data: Object.values(data),
          barThickness: 20,
          backgroundColor: `lightblue`,
          borderColor: `blue`,
          borderWidth: 1,
        }
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Categories",
          },
        },
        y: {
          beginAtZero: true,

        },
      },
    },
  });
};


const global_demography_category_oblasts = (JSONSting) => {
  const ctx = document.getElementById("global_demography_category_oblasts");
  const data = JSON.parse(
    JSONSting
  );

  const activities = Array.from(
    new Set(Object.values(data).flatMap(region => Object.keys(region)))
  );
  
  const primaryLabels = Object.keys(data); // Get the outer keys as primary labels
  
  const datasets = activities.map((activity) => {
    return {
      label: activity,
      data: primaryLabels.map((primaryLabel) => {
        return data[primaryLabel][activity] || 0;
      }),
      backgroundColor: `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${
        Math.random() * 255
      }, 0.7)`,
      borderColor: `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${
        Math.random() * 255
      }, 1)`,
      borderWidth: 1,
    };
  });
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: primaryLabels,
      datasets: datasets
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Regions",
          },
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Total benefeciaries"
          }
        },
      },
    },
  });
};


const global_age_category = (JSONSting) => {
  const ctx = document.getElementById("global_age_category");
  const data = JSON.parse(
    JSONSting
  );

  const ageGroups = Array.from(
    new Set(Object.values(data).flatMap(activity => Object.keys(activity)))
  );
  
  const activityLabels = Object.keys(data); // Get the outer keys as activity labels
  
  const datasets = ageGroups.map((ageGroup) => {
    return {
      label: ageGroup,
      data: activityLabels.map((activityLabel) => {
        return data[activityLabel][ageGroup] || 0;
      }),
      backgroundColor: `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${
        Math.random() * 255
      }, 0.7)`,
      borderColor: `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${
        Math.random() * 255
      }, 1)`,
      borderWidth: 1,
    };
  });
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: activityLabels,
      datasets: datasets
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Regions",
          },
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Total benefeciaries"
          }
        },
      },
    },
  });
};

const global_gender = (JSONSting) => {
  const ctx = document.getElementById("global_gender");
  const genderData = JSON.parse(JSONSting); // Replace 'gender_data' with the variable containing your gender data.

  // Create a doughnut chart for gender data.
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: Object.keys(genderData),
      datasets: [
        {
          data: Object.values(genderData),
          backgroundColor: [
            "rgba(75, 192, 192, 0.7)",
            "rgba(255, 99, 132, 0.7)",
          ], // You can customize the colors here.
          borderColor: ["rgba(75, 192, 192, 1)", "rgba(255, 99, 132, 1)"],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          position: "bottom",
        },
      },
    },
  });
};

const family_oblast = (JSONSting) => {
  const ctx = document.getElementById("family_oblast");
  const data = JSON.parse(
    JSONSting
  );

  const regions = Object.keys(data); 
  const values = Object.values(data); 
  
  const datasets = [{
    label: 'Household average',
    data: values,
    backgroundColor: `lightblue`,
    borderColor: `blue`,
    borderWidth: 1,
  }];
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: regions,
      datasets: datasets
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Household average",
          },
        },
        y: {
          beginAtZero: true,

        },
      },
    },
  });
};

const family_category = (JSONSting) => {
  const ctx = document.getElementById("family_category");
  const data = JSON.parse(
    JSONSting
  );

  const categories = Object.keys(data); 
  const values = Object.values(data); 
  
  const datasets = [{
    label: 'Household average',
    data: values,
    backgroundColor: `pink`,
    borderColor: `red`,
    borderWidth: 1,
  }];
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: categories,
      datasets: datasets
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Household average",
          },
        },
        y: {
          beginAtZero: true,

        },
      },
    },
  });
};

const pwd_oblast = (JSONSting) => {
  const ctx = document.getElementById("pwd_oblast");
  const data = JSON.parse(
    JSONSting
  );

  const categories = Object.keys(data); 
  const values = Object.values(data); 
  
  const datasets = [{
    label: 'PWD Percentage',
    data: values,
    backgroundColor: `red`,
    borderColor: `red`,
    borderWidth: 1,
  }];
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: categories,
      datasets: datasets
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "PWD Percentage",
          },
        },
        y: {
          beginAtZero: true,

        },
      },
    },
  });
};

const pwd_category = (JSONSting) => {
  const ctx = document.getElementById("pwd_category");
  const data = JSON.parse(
    JSONSting
  );

  const categories = Object.keys(data); 
  const values = Object.values(data); 
  
  const datasets = [{
    label: 'PWD Percentage',
    data: values,
    backgroundColor: `green`,
    borderColor: `green`,
    borderWidth: 1,
  }];
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: categories,
      datasets: datasets
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "PWD Percentage",
          },
        },
        y: {
          beginAtZero: true,

        },
      },
    },
  });
};

const children_oblast = (JSONSting) => {
  const ctx = document.getElementById("children_oblast");
  const data = JSON.parse(
    JSONSting
  );

  const regions = Object.keys(data); 
  const values = Object.values(data); 
  
  const datasets = [{
    label: 'Children average',
    data: values,
    backgroundColor: `purple`,
    borderColor: `purple`,
    borderWidth: 1,
  }];
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: regions,
      datasets: datasets
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Children average",
          },
        },
        y: {
          beginAtZero: true,

        },
      },
    },
  });
};

const time_benef = (JSONString) => {
  const ctx = document.getElementById("time_benef");
  const data = JSON.parse(JSONString);

  // Extracting unique dates from all regions and sorting them chronologically
  let datesSet = new Set();
  for (const region in data) {
    if (Object.hasOwnProperty.call(data, region)) {
      const regionDates = Object.keys(data[region]);
      regionDates.forEach(date => datesSet.add(date));
    }
  }

  const sortedDates = Array.from(datesSet).sort((a, b) => {
    const [aMonth, aYear] = a.split('-');
    const [bMonth, bYear] = b.split('-');
    return new Date(`${aYear}-${aMonth}-01`) - new Date(`${bYear}-${bMonth}-01`);
  });

  const datasets = [];

  for (const region in data) {
    if (Object.hasOwnProperty.call(data, region)) {
      const regionValues = [];

      sortedDates.forEach(date => {
        regionValues.push(data[region][date] || 0); // Fill missing values with 0
      });

      const color = `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 1)`;
      datasets.push({
        label: region,
        data: regionValues,
        backgroundColor: color,
        borderColor: color,
        borderWidth: 1,
        tension: 0.2
      });
    }
  }

  new Chart(ctx, {
    type: "line",
    data: {
      labels: sortedDates,
      datasets: datasets,
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: "Time",
          },
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Benefeciaries",
          },
        },
      },
    },
  });
};


const time_benef_category = (JSONString) => {
  const ctx = document.getElementById("time_benef_category");
  const data = JSON.parse(JSONString);

  // Extracting unique dates from all regions and sorting them chronologically
  let datesSet = new Set();
  for (const category in data) {
    if (Object.hasOwnProperty.call(data, category)) {
      const categoryDates = Object.keys(data[category]);
      categoryDates.forEach(date => datesSet.add(date));
    }
  }

  const sortedDates = Array.from(datesSet).sort((a, b) => {
    const [aMonth, aYear] = a.split('-');
    const [bMonth, bYear] = b.split('-');
    return new Date(`${aYear}-${aMonth}-01`) - new Date(`${bYear}-${bMonth}-01`);
  });

  const datasets = [];

  for (const category in data) {
    if (Object.hasOwnProperty.call(data, category)) {
      const categoryValues = [];

      sortedDates.forEach(date => {
        categoryValues.push(data[category][date] || 0); // Fill missing values with 0
      });

      const color = `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 1)`;
      datasets.push({
        label: category,
        data: categoryValues,
        backgroundColor: color,
        borderColor: color,
        borderWidth: 1,
        tension: 0.2
      });
    }
  }

  new Chart(ctx, {
    type: "line",
    data: {
      labels: sortedDates,
      datasets: datasets,
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: "Time",
          },
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Benefeciaries",
          },
        },
      },
    },
  });
};


const children_category = (JSONSting) => {
  const ctx = document.getElementById("children_category");
  const data = JSON.parse(
    JSONSting
  );

  const categories = Object.keys(data); 
  const values = Object.values(data); 
  
  const datasets = [{
    label: 'Children average',
    data: values,
    backgroundColor: `yellow`,
    borderColor: `yellow`,
    borderWidth: 1,
  }];
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: categories,
      datasets: datasets
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Children average",
          },
        },
        y: {
          beginAtZero: true,

        },
      },
    },
  });
};


export default {
  global_demography_category,
  global_demography_category_oblasts,
  global_age_category,
  global_gender,
  family_oblast,
  family_category,
  pwd_oblast,
  pwd_category,
  children_oblast,
  children_category,
  time_benef,
  time_benef_category,
};

