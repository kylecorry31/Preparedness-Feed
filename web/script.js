const notificationsKey = "notifications2";

async function getUrl(url, type) {
  const response = await fetch(url);
  const text = await response.text();
  if (type === "xml") {
    return parseXml(text);
  } else if (type === "html") {
    return parseHtml(text);
  } else if (type === "json") {
    return JSON.parse(text);
  } else {
    return text;
  }
}

function parseXml(xml) {
  const parser = new DOMParser();
  return parser.parseFromString(xml, "text/xml");
}

function parseHtml(html) {
  const parser = new DOMParser();
  return parser.parseFromString(html, "text/html");
}

function parseRSS(xml) {
  const items = [];
  xml.querySelectorAll("item").forEach((item) => {
    items.push({
      title: item.querySelector("title").textContent,
      link: item.querySelector("link").textContent,
      guid: item.querySelector("guid").textContent,
      pub_date: new Date(item.querySelector("pubDate").textContent).getTime(),
      summary: item.querySelector("description").textContent,
    });
  });
  return items;
}

function parseAtom(atom, additionalFields) {
  const items = [];
  atom.querySelectorAll("entry").forEach((entry) => {
    items.push({
      title: entry.querySelector("title").textContent,
      link: entry.querySelector("link").getAttribute("href"),
      guid: entry.querySelector("id").textContent,
      pub_date: new Date(entry.querySelector("updated").textContent).getTime(),
      summary: entry.querySelector("summary").textContent,
      ...additionalFields.reduce((acc, field) => {
        acc[field] = entry.querySelector(field).textContent;
        return acc;
      }, {}),
    });
  });
  return items;
}

async function getSWPCNotifications() {
  const serialRegex = /Serial Number:\s([0-9]+)/;
  const titleRegex = /(WARNING|ALERT|SUMMARY|WATCH):\s(.*)/;

  const url = "https://services.swpc.noaa.gov/products/alerts.json";
  const alerts = await getUrl(url, "json");
  const items = [];
  for (const alert of alerts) {
    const productId = alert.product_id;
    const message = alert.message;
    if (!message.includes("WATCH: Geomagnetic Storm Category")) {
      continue;
    }
    const serialNumber = message.match(serialRegex)[1];
    const title = message.match(titleRegex)[2];
    const date = new Date(alert.issue_datetime + "Z").getTime();
    if (date < new Date().getTime() - 7 * 24 * 3600) {
      continue;
    }
    items.push({
      title: title,
      link: "https://www.swpc.noaa.gov/",
      guid: serialNumber,
      pub_date: date,
      summary: message,
      source: "SWPC",
      type: productId,
    });
  }

  return items;
}

async function getExecutiveOrdersNotifications() {
  const url =
    "https://www.federalregister.gov/api/v1/documents?conditions%5Bpresidential_document_type%5D%5B%5D=executive_order&conditions%5Btype%5D%5B%5D=PRESDOCU&fields%5B%5D=executive_order_number&fields%5B%5D=body_html_url&fields%5B%5D=publication_date&fields%5B%5D=title&format=json&order=newest&per_page=20";
  const json = await getUrl(url, "json");

  const items = [];

  for (const document of json.results) {
    const title = document.title;
    const link = document.body_html_url;
    const date = new Date(document.publication_date).getTime();
    items.push({
      title: title,
      link: link,
      guid: document.executive_order_number,
      pub_date: date,
      source: "Federal Register",
      type: "Executive Order",
      canSummarize: false,
    });
  }

  return items;
}

async function getHealthAlertNetworkNotifications() {
  const url = "https://www.cdc.gov/han/index.html";
  const html = await getUrl(url, "html");

  const items = [];
  html.querySelectorAll(".bg-quaternary .card").forEach((card) => {
    const titleElement = card.querySelector("a");
    if (titleElement == null) {
      return;
    }
    const title = titleElement.textContent;
    const link = titleElement.href.replace("file://", "");
    const dateElement = card.querySelector("p");
    if (dateElement == null) {
      return;
    }
    let date = dateElement.textContent;
    let hasDate = false;
    while (date.length > 0) {
      try {
        let newDate = new Date(date).getTime();
        if (Number.isNaN(newDate)) {
          throw new Error("Invalid Date");
        }
        date = newDate;
        hasDate = true;
        break;
      } catch (e) {
        date = date.slice(1);
      }
    }

    if (!hasDate) {
      return;
    }

    items.push({
      title: title,
      link: "https://www.cdc.gov" + link,
      guid: link.split("/").pop().replace(".html", ""),
      pub_date: date,
      source: "CDC",
      type: "Alert",
    });
  });

  return items;
}

async function getNationalWeatherServiceNotifications(area) {
  const url = "https://api.weather.gov/alerts/active.atom?area=" + area;
  const xml = await getUrl(url, "xml");
  const items = parseAtom(xml, ["msgType"]);
  items.forEach((item) => {
    item.source = "NWS";
    item.type = item.msgType;
    item.useSummary = true;
  });
  return items;
}

function getCachedNotifications() {
  // Retrieve from local storage
  let notifications = JSON.parse(localStorage.getItem(notificationsKey));
  if (notifications == null) {
    return [];
  }

  // Delete old notifications (older than 100 days)
  notifications = notifications.filter((notification) => {
    return (
      notification.pub_date > new Date().getTime() - 100 * 24 * 3600 * 1000
    );
  });

  saveNotifications(notifications);

  return notifications;
}

function saveNotifications(notifications) {
  // Save to local storage
  localStorage.setItem(notificationsKey, JSON.stringify(notifications));
}

function getArea() {
  return localStorage.getItem("area");
}

function setArea(area) {
  localStorage.setItem("area", area);
}

function getGeminiApiKey() {
  return localStorage.getItem("geminiApiKey");
}

function setGeminiApiKey(apiKey) {
  localStorage.setItem("geminiApiKey", apiKey);
}

async function summarizeText(text) {
  const apiKey = getGeminiApiKey();
  const result = await fetch(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" +
      apiKey,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              {
                text: `Write a concise summary of the following text:\n\n${text}`,
              },
            ],
          },
        ],
      }),
    },
  );

  const json = await result.json();

  // Artificial delay for rate limiting
  await new Promise((resolve) => setTimeout(resolve, 500));

  return json.candidates[0].content.parts[0].text;
}

async function summarizeLink(link) {
  const html = await getUrl(link, "html");
  return summarizeText(html.querySelector("body").textContent);
}

async function update() {
  const container = document.getElementById("container");
  container.innerHTML = "Updating...";

  const cached = getCachedNotifications();
  const items = await getNationalWeatherServiceNotifications(getArea());
  items.push(...(await getSWPCNotifications()));
  items.push(...(await getExecutiveOrdersNotifications()));
  items.push(...(await getHealthAlertNetworkNotifications()));
  let newItems = items.filter((item) => {
    const match = cached.find(
      (i) => i.guid === item.guid && i.source === item.source,
    );

    if (match != null && match.pub_date < item.pub_date) {
      cached.splice(cached.indexOf(match), 1);
      return true;
    }

    // If the item is older than a week, don't add it
    if (item.pub_date < new Date().getTime() - 7 * 24 * 3600 * 1000) {
      return false;
    }

    return match == null;
  });

  const failedItems = [];
  for (let item of newItems) {
    try {
      if (item.canSummarize === false) {
        // Do nothing
      } else if (item.useSummary) {
        item.summary = await summarizeText(item.summary);
      } else {
        item.summary = await summarizeLink(item.link, item.useCors ?? true);
      }
    } catch (e) {
      failedItems.push(item);
    }
  }

  // Remove failed items
  newItems = newItems.filter((item) => !failedItems.includes(item));

  if (failedItems.length > 0) {
    console.log("The following items failed", failedItems);
  }

  saveNotifications([...cached, ...newItems]);

  showNotifications();
}

function showNotifications() {
  const cached = getCachedNotifications();
  cached.sort((a, b) => b.pub_date - a.pub_date);
  const container = document.getElementById("container");
  container.innerHTML = "";

  const updateButton = document.createElement("button");
  updateButton.textContent = "Update";
  updateButton.onclick = update;
  container.appendChild(updateButton);

  const clearButton = document.createElement("button");
  clearButton.textContent = "Clear";
  clearButton.onclick = () => {
    localStorage.removeItem(notificationsKey);
    showNotifications();
  };
  container.appendChild(clearButton);

  const apiKeyLabel = document.createElement("label");
  apiKeyLabel.textContent = "Gemini API Key";
  container.appendChild(apiKeyLabel);

  const apiKeyInput = document.createElement("input");
  apiKeyInput.placeholder = "Gemini API Key";
  apiKeyInput.type = "password";
  apiKeyInput.value = getGeminiApiKey();
  apiKeyInput.oninput = () => {
    setGeminiApiKey(apiKeyInput.value);
  };
  container.appendChild(apiKeyInput);

  const areaLabel = document.createElement("label");
  areaLabel.textContent = "NWS Area";
  container.appendChild(areaLabel);

  const areaInput = document.createElement("input");
  areaInput.placeholder = "NWS Area";
  areaInput.value = getArea();
  areaInput.oninput = () => {
    setArea(areaInput.value);
  };
  container.appendChild(areaInput);

  for (const item of cached) {
    const div = document.createElement("div");
    div.innerHTML = `
      <h3>${item.title}</h3>
      <p>${item.summary}</p>
      <p>${item.source}</p>
    `;
    container.appendChild(div);
  }
}

showNotifications();
