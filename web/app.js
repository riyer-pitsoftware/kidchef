const API_BASE = window.KIDS_CHEF_API_BASE || "/api";
const STORAGE_KEY = "kidschef.mvp.state.v1";
const API_SOURCE = "api";
const OFFLINE_SOURCE = "offline";
const API_REQUEST_TIMEOUT_MS = 65000;

const MEALS = [
  { key: "breakfast", label: "Breakfast", hint: "Quick starts, easy wins." },
  { key: "lunch", label: "Lunch", hint: "Simple handheld or bowl meals." },
  { key: "dinner", label: "Dinner", hint: "Bigger, calm step-by-step recipes." },
  { key: "snack", label: "Snack", hint: "Fast, small, and fun." },
];

const FILTER_OPTIONS = {
  allergens: [
    "dairy",
    "egg",
    "wheat",
    "peanut",
    "tree_nut",
    "soy",
    "fish",
    "shellfish",
    "sesame",
  ],
  diets: ["vegetarian", "vegan", "dairy_free", "gluten_free", "egg_free"],
  appliances: ["microwave", "toaster", "air_fryer", "blender", "hand_mixer", "stand_mixer", "food_processor"],
};

const DEFAULT_STATE = {
  route: "meal",
  mealType: "breakfast",
  ingredientInput: "",
  ingredients: [],
  filters: {
    allergens: [],
    diets: [],
    appliances: [],
  },
  safetyMode: "standard",
  recipes: [],
  suggestions: [],
  selectedRecipeId: null,
  favorites: [],
  apiStatus: "loading",
  apiMessage: "Loading local data…",
  busy: false,
  busyMessage: "",
  busyStartedAt: 0,
  busyDeadlineAt: 0,
  busyTimedOut: false,
  busyTick: null,
  timer: null,
  timerTick: null,
  activeStepIndex: 0,
  source: OFFLINE_SOURCE,
};

const state = loadSavedState();
const app = document.getElementById("app");

function loadSavedState() {
  const saved = safeParse(localStorage.getItem(STORAGE_KEY)) || {};
  return {
    ...DEFAULT_STATE,
    mealType: saved.mealType || DEFAULT_STATE.mealType,
    ingredientInput: "",
    ingredients: Array.isArray(saved.ingredients) ? saved.ingredients : DEFAULT_STATE.ingredients,
    filters: mergeFilters(saved.filters),
    safetyMode: saved.safetyMode || DEFAULT_STATE.safetyMode,
    favorites: Array.isArray(saved.favorites) ? saved.favorites : DEFAULT_STATE.favorites,
    recipes: [],
    suggestions: [],
    selectedRecipeId: null,
  };
}

function mergeFilters(filters) {
  return {
    allergens: Array.isArray(filters?.allergens) ? filters.allergens : [],
    diets: Array.isArray(filters?.diets) ? filters.diets : [],
    appliances: Array.isArray(filters?.appliances) ? filters.appliances : [],
  };
}

function safeParse(value) {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function persistState() {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      mealType: state.mealType,
      ingredients: state.ingredients,
      filters: state.filters,
      safetyMode: state.safetyMode,
      favorites: state.favorites,
    }),
  );
}

function invalidateSuggestions() {
  state.suggestions = [];
  if (state.route === "suggestions") {
    state.selectedRecipeId = null;
  }
}

function setState(patch) {
  Object.assign(state, patch);
  persistState();
  render();
}

function toggleInArray(list, value) {
  return list.includes(value) ? list.filter((item) => item !== value) : [...list, value];
}

function normalizeToken(value) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, " ");
}

function escapeHTML(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function joinList(values) {
  return values.filter(Boolean).join(", ");
}

function formatTimer(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;
  if (minutes === 0) {
    return `${remaining}s`;
  }
  return remaining === 0 ? `${minutes}m` : `${minutes}m ${remaining}s`;
}

function formatRoute(route) {
  switch (route) {
    case "meal":
      return "Meal";
    case "ingredients":
      return "Ingredients";
    case "filters":
      return "Filters";
    case "suggestions":
      return "Suggestions";
    case "recipe":
      return "Recipe";
    case "stepper":
      return "Cooking";
    case "favorites":
      return "Favorites";
    default:
      return "KidsChef";
  }
}

function isDemoMode() {
  return state.apiStatus !== "ready";
}

async function apiRequest(path, options = {}) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), API_REQUEST_TIMEOUT_MS);
  let response;

  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
      signal: controller.signal,
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error("request_timeout");
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }

  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }

  return response.json();
}

function normalizeRecipe(recipe) {
  return {
    ...recipe,
    source: recipe.source || "curated",
    validation_status: recipe.validation_status || "validated",
    ingredients: Array.isArray(recipe.ingredients) ? recipe.ingredients : [],
    steps: Array.isArray(recipe.steps) ? recipe.steps : [],
    appliances: Array.isArray(recipe.appliances) ? recipe.appliances : [],
    allergens: Array.isArray(recipe.allergens) ? recipe.allergens : [],
    diet_tags: Array.isArray(recipe.diet_tags) ? recipe.diet_tags : [],
    safety_flags: Array.isArray(recipe.safety_flags) ? recipe.safety_flags : [],
  };
}

function safetyAllowsRecipe(recipe) {
  const safetyFlags = new Set(recipe.safety_flags || []);
  const requiresAdultHelp = Boolean(recipe.adult_help_required);
  const strictBlocked = ["knife", "stove", "oven"].some((flag) => safetyFlags.has(flag));

  if (state.safetyMode === "strict" && strictBlocked) {
    return { allowed: false, reason: "This recipe uses a blocked stove, oven, or knife step." };
  }

  if (state.safetyMode === "standard" && requiresAdultHelp && strictBlocked) {
    return { allowed: true, reason: "This recipe needs adult help." };
  }

  return { allowed: true, reason: requiresAdultHelp ? "This recipe needs adult help." : "Safe for the current mode." };
}

function filtersAllowRecipe(recipe) {
  const blockedAllergens = state.filters.allergens;
  const requiredDiets = state.filters.diets;
  const availableAppliances = state.filters.appliances;

  if (recipe.allergens.some((item) => blockedAllergens.includes(item))) {
    return { allowed: false, reason: "It contains a blocked allergen." };
  }

  if (requiredDiets.length && !requiredDiets.every((diet) => recipe.diet_tags.includes(diet))) {
    return { allowed: false, reason: "It does not match the selected diet filters." };
  }

  if (
    availableAppliances.length &&
    recipe.appliances.some((appliance) => !availableAppliances.includes(appliance))
  ) {
    return { allowed: false, reason: "It needs an appliance that is not available." };
  }

  return { allowed: true, reason: "" };
}

function ingredientMatchReasons(recipe) {
  const chosen = new Set(state.ingredients.map((item) => normalizeToken(item)));
  const matches = recipe.ingredients
    .map((ingredient) => ingredient.name)
    .filter((name) => chosen.has(normalizeToken(name)));

  return matches.length ? [`Uses ${joinList(matches)}`] : [];
}

function recipeUsesOnlyChosenIngredients(recipe) {
  if (!state.ingredients.length) {
    return true;
  }
  const chosen = new Set(state.ingredients.map((item) => normalizeToken(item)));
  const required = recipe.ingredients
    .filter((ingredient) => !ingredient.optional)
    .map((ingredient) => normalizeToken(ingredient.name))
    .filter(Boolean);

  if (!required.length) {
    return false;
  }

  return required.every((name) => chosen.has(name));
}

function missingIngredientsForRecipe(recipe) {
  const chosen = new Set(state.ingredients.map((item) => normalizeToken(item)));
  return recipe.ingredients
    .filter((ingredient) => !ingredient.optional)
    .map((ingredient) => normalizeToken(ingredient.name))
    .filter((name) => name && !chosen.has(name));
}

function recipeCardReasons(recipe) {
  const reasons = [
    recipe.meal_type === state.mealType ? `${capitalize(recipe.meal_type)} match` : "",
    ...ingredientMatchReasons(recipe),
    recipe.source === "ai_derived" ? "Local AI suggestion" : "Curated recipe",
  ].filter(Boolean);

  return reasons.slice(0, 3);
}

function capitalize(value) {
  return String(value).charAt(0).toUpperCase() + String(value).slice(1);
}

function computeSuggestions() {
  const safe = [];
  const possible = [];
  const blocked = [];

  for (const recipe of state.recipes) {
    if (recipe.meal_type !== state.mealType) {
      continue;
    }

    const filterCheck = filtersAllowRecipe(recipe);
    const safetyCheck = safetyAllowsRecipe(recipe);
    const pantryAllowed = recipeUsesOnlyChosenIngredients(recipe);
    const missingIngredients = pantryAllowed ? [] : missingIngredientsForRecipe(recipe);
    const reasons = recipeCardReasons(recipe);

    if (pantryAllowed && filterCheck.allowed && safetyCheck.allowed && recipe.validation_status !== "rejected") {
      safe.push({
        ...recipe,
        availabilityState: "ready",
        cardReasons: reasons.length ? reasons : ["Good match"],
      });
      continue;
    }

    if (!pantryAllowed && filterCheck.allowed && safetyCheck.allowed && recipe.validation_status !== "rejected") {
      possible.push({
        ...recipe,
        availabilityState: "possible",
        missingIngredients,
        possibleReason:
          missingIngredients.length === 1
            ? `This could work if a parent adds ${missingIngredients[0]}.`
            : `This could work if a parent adds ${joinList(missingIngredients)}.`,
        cardReasons: reasons.length ? reasons : ["Possible with more ingredients"],
      });
      continue;
    }

    blocked.push({
      ...recipe,
      availabilityState: "blocked",
      blockedReason: !filterCheck.allowed
        ? filterCheck.reason
        : !safetyCheck.allowed
          ? safetyCheck.reason
          : "This recipe is not available in the current mode.",
      cardReasons: reasons.length ? reasons : ["Does not fit the current rules"],
    });
  }

  return { safe, possible, blocked };
}

function currentRecipe() {
  return state.recipes.find((recipe) => recipe.recipe_id === state.selectedRecipeId) || null;
}

function currentStep() {
  const recipe = currentRecipe();
  if (!recipe) return null;
  return recipe.steps[state.activeStepIndex] || recipe.steps[0] || null;
}

function startTimer(durationSeconds, label) {
  clearTimer();
  const endAt = Date.now() + durationSeconds * 1000;
  state.timer = {
    label,
    durationSeconds,
    endAt,
    finished: false,
  };
  persistState();
  render();

  state.timerTick = window.setInterval(() => {
    const remaining = Math.max(0, Math.ceil((state.timer.endAt - Date.now()) / 1000));
    if (remaining <= 0) {
      clearTimer(false);
      state.timer = {
        ...state.timer,
        finished: true,
        remaining: 0,
      };
      render();
      return;
    }

    state.timer.remaining = remaining;
    render();
  }, 1000);
}

function clearTimer(reset = true) {
  if (state.timerTick) {
    clearInterval(state.timerTick);
    state.timerTick = null;
  }
  if (reset) {
    state.timer = null;
  }
}

function syncTimerFromClock() {
  if (!state.timer?.endAt) return;
  const remaining = Math.max(0, Math.ceil((state.timer.endAt - Date.now()) / 1000));
  state.timer.remaining = remaining;
  state.timer.finished = remaining === 0;
  if (remaining === 0 && state.timerTick) {
    clearTimer(false);
  }
}

function startBusy(message, timeoutMs = API_REQUEST_TIMEOUT_MS) {
  if (state.busyTick) {
    clearInterval(state.busyTick);
  }
  state.busy = true;
  state.busyMessage = message;
  state.busyStartedAt = Date.now();
  state.busyDeadlineAt = state.busyStartedAt + timeoutMs;
  state.busyTimedOut = false;
  state.busyTick = window.setInterval(() => {
    if (!state.busy) {
      stopBusy();
      return;
    }
    render();
  }, 250);
}

function stopBusy() {
  if (state.busyTick) {
    clearInterval(state.busyTick);
    state.busyTick = null;
  }
  state.busy = false;
  state.busyMessage = "";
  state.busyStartedAt = 0;
  state.busyDeadlineAt = 0;
  state.busyTimedOut = false;
}

function markBusyTimedOut(message) {
  state.busyTimedOut = true;
  state.busyMessage = message;
  render();
}

async function bootstrap() {
  state.apiStatus = "loading";
  state.apiMessage = "Connecting to the local API…";
  render();

  try {
    const data = await apiRequest("/bootstrap");
    state.recipes = (Array.isArray(data.recipes) ? data.recipes : []).map(normalizeRecipe);
    state.favorites = Array.isArray(data.favorites) ? data.favorites : state.favorites;
    state.safetyMode = data.safetyMode || state.safetyMode;
    state.apiStatus = "ready";
    state.apiMessage = "Connected to the local API.";
    state.source = API_SOURCE;
  } catch {
    state.recipes = [];
    state.apiStatus = "degraded";
    state.apiMessage = "Local API unavailable. Recipe generation needs Ollama.";
    state.source = OFFLINE_SOURCE;
  }

  persistState();
  render();
}

async function retryApiConnection() {
  if (state.busy || state.apiStatus === "loading") {
    return;
  }

  startBusy("Trying the local API again…", 12000);
  render();

  try {
    await bootstrap();
  } finally {
    stopBusy();
    render();
  }
}

async function findRecipes() {
  state.route = "suggestions";
  startBusy("Filling your cake with ideas…");
  persistState();
  render();

  syncTimerFromClock();
  const payload = {
    meal_type: state.mealType,
    ingredients: state.ingredients,
    allergens: state.filters.allergens,
    diet_tags: state.filters.diets,
    appliances: state.filters.appliances,
    safety_mode: state.safetyMode,
  };

  try {
    const data = await apiRequest("/recommendations", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    const results = (Array.isArray(data.recipes) ? data.recipes : []).map(normalizeRecipe);
    state.recipes = results;
    state.suggestions = results;
    state.apiStatus = "ready";
    state.apiMessage = "Connected to the local API.";
  } catch (error) {
    if (error instanceof Error && error.message === "request_timeout") {
      markBusyTimedOut("The cake ran out of time waiting for Ollama.");
    }
    state.suggestions = [];
    state.apiStatus = "degraded";
    state.apiMessage =
      state.source === API_SOURCE
        ? "Live generation timed out or failed. No local recipe fallback is available."
        : "Local API unavailable. Recipe generation needs Ollama.";
  }

  stopBusy();
  state.route = "suggestions";
  persistState();
  render();
}

function selectRecipe(recipeId, startCooking = false) {
  state.selectedRecipeId = recipeId;
  state.activeStepIndex = 0;
  clearTimer();
  state.timer = null;
  state.route = startCooking ? "stepper" : "recipe";
  persistState();
  render();
}

async function loadRecipeDetail(recipeId, startCooking = false) {
  const existing = state.recipes.find((item) => item.recipe_id === recipeId);
  if (existing && !existing.summary_only && Array.isArray(existing.steps) && existing.steps.length) {
    selectRecipe(recipeId, startCooking);
    return;
  }

  startBusy("Mixing the full recipe…", 45000);
  render();
  try {
    const data = await apiRequest(`/recipes/${encodeURIComponent(recipeId)}`);
    const recipe = normalizeRecipe(data.recipe || {});
    const index = state.recipes.findIndex((item) => item.recipe_id === recipeId);
    if (index >= 0) {
      state.recipes[index] = recipe;
    } else {
      state.recipes.push(recipe);
    }
    if (state.suggestions.some((item) => item.recipe_id === recipeId)) {
      state.suggestions = state.suggestions.map((item) => (item.recipe_id === recipeId ? recipe : item));
    }
    stopBusy();
    selectRecipe(recipeId, startCooking);
  } catch (error) {
    if (error instanceof Error && error.message === "request_timeout") {
      markBusyTimedOut("The cake ran out of time finishing the recipe.");
    }
    stopBusy();
    state.apiStatus = "degraded";
    state.apiMessage = "Recipe details took too long to generate.";
    render();
  }
}

async function toggleFavorite(recipeId) {
  const set = new Set(state.favorites);
  if (set.has(recipeId)) {
    set.delete(recipeId);
  } else {
    set.add(recipeId);
  }
  state.favorites = Array.from(set);
  persistState();
  render();

  if (state.apiStatus === "ready") {
    try {
      const data = await apiRequest("/favorites/toggle", {
        method: "POST",
        body: JSON.stringify({ recipeId }),
      });
      state.favorites = Array.isArray(data.favorites) ? data.favorites : state.favorites;
      state.apiStatus = "ready";
      state.apiMessage = "Connected to the local API.";
      persistState();
      render();
    } catch {
      state.apiStatus = "degraded";
      state.apiMessage =
        "Favorite saved on this device, but the local API is unavailable so it may not sync household-wide yet.";
      persistState();
      render();
    }
  }
}

function goRoute(route) {
  if (route === "stepper") {
    state.route = "recipe";
  } else {
    state.route = route;
  }
  persistState();
  render();
}

function addIngredient(value) {
  const parsed = value
    .split(/[,;\n]/)
    .map(normalizeToken)
    .filter(Boolean);

  if (!parsed.length) {
    return;
  }

  const ingredients = [...state.ingredients];
  for (const item of parsed) {
    if (!ingredients.includes(item)) {
      ingredients.push(item);
    }
  }

  state.ingredients = ingredients;
  state.ingredientInput = "";
  invalidateSuggestions();
  persistState();
  render();
}

function removeIngredient(value) {
  state.ingredients = state.ingredients.filter((item) => item !== value);
  invalidateSuggestions();
  persistState();
  render();
}

function toggleFilter(group, value) {
  state.filters = {
    ...state.filters,
    [group]: toggleInArray(state.filters[group], value),
  };
  invalidateSuggestions();
  persistState();
  render();
}

function setMealType(mealType) {
  state.mealType = mealType;
  invalidateSuggestions();
  persistState();
  render();
}

function goNextFromMeal() {
  state.route = "ingredients";
  persistState();
  render();
}

function goBackFromIngredients() {
  state.route = "meal";
  persistState();
  render();
}

function goBackFromFilters() {
  state.route = "ingredients";
  persistState();
  render();
}

function goBackFromRecipe() {
  state.route = "suggestions";
  persistState();
  render();
}

function goBackFromStepper() {
  state.route = "recipe";
  clearTimer();
  state.timer = null;
  persistState();
  render();
}

function stepForward() {
  const recipe = currentRecipe();
  if (!recipe) return;
  if (state.activeStepIndex < recipe.steps.length - 1) {
    state.activeStepIndex += 1;
    clearTimer();
    state.timer = null;
    persistState();
    render();
    return;
  }

  state.route = "recipe";
  clearTimer();
  state.timer = null;
  persistState();
  render();
}

function stepBackward() {
  if (state.activeStepIndex > 0) {
    state.activeStepIndex -= 1;
    clearTimer();
    state.timer = null;
    persistState();
    render();
  }
}

function repeatStep() {
  clearTimer();
  state.timer = null;
  persistState();
  render();
}

function renderChips(values, tone = "default") {
  return values
    .map(
      (value) => `<span class="tag ${tone === "soft" ? "tag--soft" : tone === "warn" ? "tag--warn" : ""}">${escapeHTML(value)}</span>`,
    )
    .join("");
}

function renderStatusChips() {
  const apiTone = state.apiStatus === "ready" ? "accent" : state.apiStatus === "degraded" ? "warn" : "quiet";
  const apiLabel =
    state.apiStatus === "ready"
      ? "Local API connected"
      : state.apiStatus === "degraded"
        ? "API offline"
        : "Connecting";

  return `
    <div class="status-stack">
      <span class="chip chip--accent">Safety: ${escapeHTML(capitalize(state.safetyMode))}</span>
      <span class="chip ${apiTone === "warn" ? "chip--warn" : apiTone === "accent" ? "chip--accent" : "chip--quiet"}">${escapeHTML(apiLabel)}</span>
      <button class="chip chip--quiet" type="button" data-action="route" data-route="favorites">Favorites: ${state.favorites.length}</button>
    </div>
  `;
}

function renderBanner() {
  if (state.apiStatus === "ready") return "";
  const isLoading = state.apiStatus === "loading";
  return `
    <div class="state-card ${state.apiStatus === "degraded" ? "step-card--help" : ""}">
      <div class="badge-line">
        <span class="chip ${state.apiStatus === "degraded" ? "chip--warn" : "chip--quiet"}">${isLoading ? "Connecting to local API" : "Local API unavailable"}</span>
        <span class="chip chip--quiet">Ollama required</span>
      </div>
      <h3>${escapeHTML(state.apiMessage)}</h3>
      <p class="muted">
        KidsChef now depends on local Llama generation. If Ollama or the API is offline, no recipe catalog is shown.
      </p>
      <div class="button-row">
        <button class="button button--ghost" type="button" data-action="retry-api" ${isLoading || state.busy ? "disabled" : ""}>${isLoading ? "Checking…" : "Try reconnecting"}</button>
      </div>
    </div>
  `;
}

function renderMealScreen() {
  return `
    <section class="hero-card">
      <div class="stack">
        <div class="badge-line">
          <span class="chip chip--accent">Step 1 of 6</span>
          <span class="chip chip--quiet">Choose a meal</span>
        </div>
        <div>
          <h2>What do you want to make?</h2>
          <p>Pick a meal type, then enter ingredients and filters. The shell keeps the flow short and clear on iPhone Safari.</p>
        </div>
      </div>
      <div class="meal-grid" role="list">
        ${MEALS.map(
          (meal) => `
            <button
              class="meal-option"
              type="button"
              role="listitem"
              aria-pressed="${state.mealType === meal.key ? "true" : "false"}"
              data-action="choose-meal"
              data-meal="${escapeHTML(meal.key)}"
            >
              <div class="meal-option__title">
                <span>${escapeHTML(meal.label)}</span>
                <span class="chip chip--quiet">${escapeHTML(meal.key)}</span>
              </div>
              <div class="meal-option__meta">${escapeHTML(meal.hint)}</div>
            </button>
          `,
        ).join("")}
      </div>
    </section>
    <div class="footer-actions">
      <div class="footer-actions__row">
        <button class="button button--ghost" type="button" data-action="route" data-route="favorites">View favorites</button>
        <button class="button button--primary" type="button" data-action="next-from-meal">Continue</button>
      </div>
    </div>
  `;
}

function renderIngredientsScreen() {
  return `
    <section class="grid grid--2">
      <div class="panel">
        <div class="panel__inner stack">
          <div class="panel__title">
            <div>
              <h3>Ingredients on hand</h3>
              <p>Add what you already have. Short tokens are fine.</p>
            </div>
            <span class="chip chip--quiet">Step 2</span>
          </div>
          <form id="ingredient-form" class="stack">
            <div class="field">
              <label for="ingredient-input">Add ingredients</label>
              <input
                id="ingredient-input"
                name="ingredient-input"
                type="text"
                inputmode="text"
                placeholder="e.g. oats, milk, banana"
                value="${escapeHTML(state.ingredientInput)}"
                autocomplete="off"
              />
            </div>
            <div class="button-row">
              <button class="button button--ghost" type="submit">Add ingredient</button>
              <button class="button button--primary" type="button" data-action="go-filters">Choose filters</button>
            </div>
          </form>
          <div class="stack">
            <div class="muted">Added ingredients</div>
            <div class="token-list">
              ${state.ingredients.length ? state.ingredients.map((ingredient) => `<span class="token">${escapeHTML(ingredient)}<button type="button" data-action="remove-ingredient" data-value="${escapeHTML(ingredient)}" aria-label="Remove ${escapeHTML(ingredient)}">×</button></span>`).join("") : `<div class="empty-card"><h3>No ingredients yet</h3><p class="muted">Start with a couple of ingredients you already have.</p></div>`}
            </div>
          </div>
        </div>
      </div>
      <div class="panel">
        <div class="panel__inner stack">
          <div class="panel__title">
            <div>
              <h3>Current meal</h3>
              <p>${escapeHTML(capitalize(state.mealType))}</p>
            </div>
            <span class="chip chip--accent">Calm flow</span>
          </div>
          ${renderMealSummary()}
          <div class="safety-callout">
            Safety mode only controls cooking risk. The next screens also check filters and what ingredients you have.
          </div>
          <div class="button-row">
            <button class="button button--ghost" type="button" data-action="back-from-ingredients">Back</button>
            <button class="button button--primary" type="button" data-action="go-filters">Continue</button>
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderMealSummary() {
  const selected = MEALS.find((meal) => meal.key === state.mealType) || MEALS[0];
  return `
    <div class="summary-card">
      <div class="badge-line">
        <span class="tag">${escapeHTML(selected.label)}</span>
        <span class="tag tag--soft">${escapeHTML(selected.hint)}</span>
      </div>
      <p class="muted">The shell will ask for allergy and diet filters next, then show matching suggestions one recipe at a time.</p>
    </div>
  `;
}

function renderFiltersScreen() {
  const group = (title, key, options) => `
    <div class="filter-group">
      <h4>${escapeHTML(title)}</h4>
      <div class="check-grid">
        ${options
          .map(
            (option) => `
              <label class="check">
                <input
                  type="checkbox"
                  data-action="toggle-filter"
                  data-group="${escapeHTML(key)}"
                  data-value="${escapeHTML(option)}"
                  ${state.filters[key].includes(option) ? "checked" : ""}
                />
                <span>${escapeHTML(option.replaceAll("_", " "))}</span>
              </label>
            `,
          )
          .join("")}
      </div>
    </div>
  `;

  return `
    <section class="grid grid--2">
      <div class="panel">
        <div class="panel__inner stack">
          <div class="panel__title">
            <div>
              <h3>Filters</h3>
              <p>These rules shape which recipes can be shown.</p>
            </div>
            <span class="chip chip--quiet">Step 3</span>
          </div>
          <div class="badge-line">
            <span class="chip chip--accent">Safety mode: ${escapeHTML(capitalize(state.safetyMode))}</span>
            <span class="chip chip--quiet">${state.ingredients.length} ingredients</span>
          </div>
          <div class="filter-grid">
            ${group("Block these allergens", "allergens", FILTER_OPTIONS.allergens)}
            ${group("Preferred diet tags", "diets", FILTER_OPTIONS.diets)}
            ${group("Allowed appliances", "appliances", FILTER_OPTIONS.appliances)}
          </div>
          <div class="button-row">
            <button class="button button--ghost" type="button" data-action="back-from-filters">Back</button>
            <button class="button button--primary" type="button" data-action="find-recipes">Find recipes</button>
          </div>
        </div>
      </div>
      <div class="panel">
        <div class="panel__inner stack">
          <div class="panel__title">
            <div>
              <h3>Why these filters matter</h3>
              <p>They keep the suggestions appropriate and useful.</p>
            </div>
          </div>
          <div class="stack">
            <div class="state-card">
              <div class="badge-line">
                <span class="chip chip--accent">No accounts</span>
                <span class="chip chip--quiet">Local only</span>
              </div>
              <p class="muted">The backend should keep household preferences local, while the browser only caches lightweight UI state.</p>
            </div>
            <div class="state-card">
              <div class="badge-line">
                <span class="chip chip--accent">Simple flow</span>
                <span class="chip chip--quiet">One recipe at a time</span>
              </div>
              <p class="muted">Suggestions are reviewed one at a time so kids can stay focused and avoid noisy decision points.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderSuggestionCards(recipes) {
  if (!recipes.length) {
    return `
      <div class="empty-card">
        <h3>No recipes matched yet</h3>
        <p class="muted">Try changing filters, removing an ingredient, or picking another meal type.</p>
        <div class="button-row" style="justify-content:center;">
          <button class="button button--ghost" type="button" data-action="route" data-route="filters">Change filters</button>
          <button class="button button--primary" type="button" data-action="route" data-route="ingredients">Edit ingredients</button>
        </div>
      </div>
    `;
  }

  return `
    <div class="recipe-list">
      ${recipes.map((recipe) => renderSuggestionCard(recipe)).join("")}
    </div>
  `;
}

function renderSuggestionCard(recipe) {
  const isFavorite = state.favorites.includes(recipe.recipe_id);
  const safetyCheck = safetyAllowsRecipe(recipe);
  const filterCheck = filtersAllowRecipe(recipe);
  const blocked = recipe.availabilityState === "blocked" || !safetyCheck.allowed || !filterCheck.allowed;
  const possible = recipe.availabilityState === "possible";
  const summaryTone = blocked ? "tag--warn" : possible ? "tag--accent" : "tag--soft";
  const reason = possible
    ? recipe.possibleReason
    : recipe.blockedReason || safetyCheck.reason || filterCheck.reason;
  const missingIngredients = Array.isArray(recipe.missingIngredients) ? recipe.missingIngredients : [];

  return `
    <article class="recipe-card ${blocked ? "step-card--blocked" : possible ? "step-card--help" : ""}">
      <div class="recipe-card__top">
        <div class="stack stack--tight">
          <h3 class="recipe-card__title">${escapeHTML(recipe.title)}</h3>
          <p class="recipe-card__summary">${escapeHTML(recipe.summary)}</p>
        </div>
        <button class="button button--tiny ${isFavorite ? "button--primary" : "button--ghost"}" type="button" data-action="toggle-favorite" data-recipe-id="${escapeHTML(recipe.recipe_id)}" aria-label="${isFavorite ? "Remove favorite" : "Save favorite"}">
          ${isFavorite ? "★" : "☆"}
        </button>
      </div>
      <div class="recipe-card__meta">
        <span class="tag">${escapeHTML(capitalize(recipe.meal_type))}</span>
        <span class="tag ${summaryTone}">${escapeHTML(recipe.difficulty)}</span>
        <span class="tag tag--soft">${escapeHTML(recipe.prep_time_minutes)} min prep</span>
        <span class="tag tag--soft">${escapeHTML(recipe.cook_time_minutes)} min cook</span>
        <span class="tag tag--soft">${escapeHTML(recipe.source === "ai_derived" ? "local AI" : "curated")}</span>
      </div>
      <div class="stack">
        <div class="badge-line">${renderChips(recipe.cardReasons || [], "soft")}</div>
        <div class="muted">${escapeHTML(blocked ? reason : `Matches ${joinList(recipe.cardReasons || ["your filters"])}`)}</div>
      </div>
      <div class="recipe-card__actions">
        <div class="badge-line">
          ${possible ? `<span class="mini-flag">${escapeHTML("Possible with parent help")}</span>` : recipe.adult_help_required ? `<span class="mini-flag mini-flag--warn">Adult help</span>` : `<span class="mini-flag mini-flag--good">Good fit</span>`}
          ${recipe.validation_status === "validated" ? `<span class="mini-flag">Validated</span>` : `<span class="mini-flag mini-flag--warn">Needs review</span>`}
        </div>
        ${
          possible && missingIngredients.length
            ? `
              <div class="helper-callout">
                <div class="stack stack--tight">
                  <strong>Possible if a parent can add:</strong>
                  <div class="badge-line">
                    ${missingIngredients
                      .map(
                        (ingredient) => `
                          <button class="chip chip--quiet" type="button" data-action="add-suggested-ingredient" data-value="${escapeHTML(ingredient)}">
                            + ${escapeHTML(ingredient)}
                          </button>
                        `,
                      )
                      .join("")}
                  </div>
                  <div class="button-row">
                    <button class="button button--ghost" type="button" data-action="open-recipe" data-recipe-id="${escapeHTML(recipe.recipe_id)}">Review</button>
                    <button class="button button--primary" type="button" data-action="add-all-missing" data-values="${escapeHTML(missingIngredients.join(","))}">Add all ingredients</button>
                  </div>
                </div>
              </div>
            `
            : ""
        }
        <div class="button-row">
          <button class="button button--ghost" type="button" data-action="open-recipe" data-recipe-id="${escapeHTML(recipe.recipe_id)}">${possible ? "Review" : "Open"}</button>
          <button class="button button--primary" type="button" data-action="start-cooking" data-recipe-id="${escapeHTML(recipe.recipe_id)}"${possible ? " disabled" : ""}>${possible ? "Add ingredients first" : "Cook"}</button>
        </div>
      </div>
    </article>
  `;
}

function renderSuggestionsScreen() {
  const { safe, possible, blocked } = computeSuggestions();
  const recipes = state.suggestions.length ? state.suggestions : safe;
  const hasRecipes = recipes.length > 0;
  const hasPossibleRecipes = !hasRecipes && possible.length > 0;
  const blockedRecipe = !hasRecipes && blocked[0];

  return `
    <section class="stack">
      <div class="hero-card">
        <div class="badge-line">
          <span class="chip chip--accent">Step 4</span>
          <span class="chip chip--quiet">${state.mealType}</span>
          <span class="chip chip--quiet">${state.ingredients.length} ingredients</span>
        </div>
        <div class="panel__title" style="margin:0;">
          <div>
            <h2>Suggestion review</h2>
            <p>One matching recipe at a time, with reasons that are easy to understand.</p>
          </div>
          <div class="button-row">
            <button class="button button--ghost" type="button" data-action="route" data-route="filters">Edit filters</button>
            <button class="button button--primary" type="button" data-action="route" data-route="ingredients">Edit ingredients</button>
          </div>
        </div>
      </div>
      ${
        hasRecipes
          ? renderSuggestionCards(recipes)
          : hasPossibleRecipes
            ? `
              <div class="helper-callout">
                <h3>Here is what is possible if your parent can add ingredients</h3>
                <p class="muted">These ideas fit the current rules. They just need a few more ingredients before you can start.</p>
              </div>
              ${renderSuggestionCards(possible)}
            `
          : blockedRecipe
            ? `
              <div class="state-card step-card--blocked">
                <div class="badge-line">
                  <span class="chip chip--warn">Blocked</span>
                  <span class="chip chip--quiet">${blocked.length} blocked option${blocked.length === 1 ? "" : "s"}</span>
                </div>
                <h3>${escapeHTML(blockedRecipe.title)} is not available with the current rules</h3>
                <p class="muted">${escapeHTML(blockedRecipe.blockedReason || "This recipe does not fit the current filters or cooking-safety mode.")}</p>
                <div class="button-row">
                  <button class="button button--ghost" type="button" data-action="route" data-route="filters">Change filters</button>
                  <button class="button button--primary" type="button" data-action="route" data-route="meal">Pick another meal</button>
                </div>
              </div>
            `
            : `
              <div class="empty-card">
                <h3>No suggestions yet</h3>
                <p class="muted">Add ingredients or adjust filters, then search again.</p>
                <div class="button-row" style="justify-content:center;">
                  <button class="button button--ghost" type="button" data-action="route" data-route="filters">Edit filters</button>
                  <button class="button button--primary" type="button" data-action="find-recipes">Try again</button>
                  ${state.apiStatus !== "ready" ? `<button class="button button--ghost" type="button" data-action="retry-api">Reconnect API</button>` : ""}
                </div>
              </div>
            `
      }
    </section>
  `;
}

function renderRecipeDetailScreen() {
  const recipe = currentRecipe();
  if (!recipe) {
    return renderUnavailableCard("Recipe unavailable", "Pick a suggestion first.");
  }

  const safetyCheck = safetyAllowsRecipe(recipe);
  const filterCheck = filtersAllowRecipe(recipe);
  const blocked = !safetyCheck.allowed || !filterCheck.allowed || recipe.validation_status === "rejected";

  return `
    <section class="stack">
      <div class="hero-card ${blocked ? "step-card--blocked" : ""}">
        <div class="badge-line">
          <span class="chip chip--accent">${escapeHTML(capitalize(recipe.meal_type))}</span>
          <span class="chip chip--quiet">${escapeHTML(recipe.difficulty)}</span>
          <span class="chip chip--quiet">${escapeHTML(recipe.source === "ai_derived" ? "local AI" : "curated")}</span>
        </div>
        <div class="panel__title" style="margin:0;">
          <div>
            <h2>${escapeHTML(recipe.title)}</h2>
            <p>${escapeHTML(recipe.summary)}</p>
          </div>
          <button class="button button--tiny ${state.favorites.includes(recipe.recipe_id) ? "button--primary" : "button--ghost"}" type="button" data-action="toggle-favorite" data-recipe-id="${escapeHTML(recipe.recipe_id)}">
            ${state.favorites.includes(recipe.recipe_id) ? "★" : "☆"}
          </button>
        </div>
        <div class="badge-line">
          <span class="mini-flag ${blocked ? "mini-flag--warn" : "mini-flag--good"}">${escapeHTML(blocked ? "Blocked" : "Ready")}</span>
          ${recipe.adult_help_required ? `<span class="mini-flag mini-flag--warn">Adult help required</span>` : `<span class="mini-flag mini-flag--good">Child-safe steps</span>`}
        </div>
        <div class="button-row">
          <button class="button button--ghost" type="button" data-action="route" data-route="suggestions">Back to suggestions</button>
          <button class="button button--primary" type="button" data-action="start-cooking" data-recipe-id="${escapeHTML(recipe.recipe_id)}"${blocked ? " disabled" : ""}>Start cooking</button>
        </div>
      </div>

      ${blocked ? renderBlockedState(recipe) : ""}

      <div class="grid grid--2">
        <div class="panel">
          <div class="panel__inner stack">
            <div class="panel__title">
              <div>
                <h3>Ingredients</h3>
                <p>Everything the stepper will use.</p>
              </div>
            </div>
            <ul class="list">
              ${recipe.ingredients
                .map((item) => `<li>${escapeHTML(item.amount ?? "")} ${escapeHTML(item.unit ?? "")} ${escapeHTML(item.name)}${item.optional ? " (optional)" : ""}</li>`)
                .join("")}
            </ul>
          </div>
        </div>
        <div class="panel">
          <div class="panel__inner stack">
            <div class="panel__title">
              <div>
                <h3>Safety markers</h3>
                <p>Shown before risky steps begin.</p>
              </div>
            </div>
            <div class="badge-line">
              ${recipe.safety_flags.length ? renderChips(recipe.safety_flags.map((flag) => flag.replaceAll("_", " ")), "warn") : `<span class="chip chip--accent">No safety flags</span>`}
            </div>
            <div class="muted">${escapeHTML(safetyCheck.reason)}</div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel__inner stack">
          <div class="panel__title">
            <div>
              <h3>Steps</h3>
              <p>One clear action at a time.</p>
            </div>
          </div>
          <div class="stack">
            ${recipe.steps
              .map(
                (step) => `
                  <div class="step-card ${step.safety_level === "blocked" ? "step-card--blocked" : step.safety_level === "adult_help" ? "step-card--help" : ""}">
                    <div class="step-card__top">
                      <div class="stack stack--tight">
                        <div class="badge-line">
                          <span class="tag">Step ${escapeHTML(step.order)}</span>
                          <span class="tag ${step.safety_level === "blocked" ? "tag--warn" : "tag--soft"}">${escapeHTML(step.safety_level.replace("_", " "))}</span>
                        </div>
                        <p class="step-text">${escapeHTML(step.instruction)}</p>
                      </div>
                      ${step.requires_adult_help ? `<span class="chip chip--warn">Adult help</span>` : `<span class="chip chip--quiet">Safe</span>`}
                    </div>
                    ${
                      step.timers.length
                        ? `<div class="badge-line">${renderChips(step.timers.map((timer) => `${timer.label} ${formatTimer(timer.duration_seconds)}`), "soft")}</div>`
                        : ""
                    }
                    ${step.warnings.length ? `<div class="safety-callout">${escapeHTML(joinList(step.warnings))}</div>` : ""}
                  </div>
                `,
              )
              .join("")}
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderBlockedState(recipe) {
  const safetyCheck = safetyAllowsRecipe(recipe);
  const filterCheck = filtersAllowRecipe(recipe);
  const message = recipe.blockedReason || safetyCheck.reason || filterCheck.reason;
  return `
    <div class="state-card step-card--blocked">
      <div class="badge-line">
        <span class="chip chip--warn">Blocked</span>
        <span class="chip chip--quiet">Rule check</span>
      </div>
      <h3>Why this recipe is blocked</h3>
      <p class="muted">${escapeHTML(message)}</p>
      <div class="button-row">
        <button class="button button--ghost" type="button" data-action="route" data-route="filters">Change filters</button>
        <button class="button button--primary" type="button" data-action="route" data-route="suggestions">Pick another recipe</button>
      </div>
    </div>
  `;
}

function renderStepperScreen() {
  const recipe = currentRecipe();
  if (!recipe) {
    return renderUnavailableCard("No active recipe", "Open a recipe first.");
  }

  const step = currentStep();
  const progress = recipe.steps.length ? Math.round(((state.activeStepIndex + 1) / recipe.steps.length) * 100) : 0;
  const timer = state.timer;
  const stepBlocked = step?.safety_level === "blocked";
  const adultHelp = step?.requires_adult_help;

  syncTimerFromClock();

  return `
    <section class="stepper-shell">
      <div class="hero-card">
        <div class="stepper-progress">
          <div>
            <div class="badge-line">
              <span class="chip chip--accent">Step ${state.activeStepIndex + 1} of ${recipe.steps.length}</span>
              <span class="chip chip--quiet">${escapeHTML(recipe.title)}</span>
            </div>
            <p class="muted">The stepper keeps the child on one action at a time.</p>
          </div>
          <button class="button button--ghost button--tiny" type="button" data-action="route" data-route="recipe">Recipe</button>
        </div>
        <div class="stepper-progress__bar" aria-hidden="true">
          <span class="stepper-progress__fill" style="width:${progress}%"></span>
        </div>
      </div>

      ${step ? renderStepCard(step, adultHelp, stepBlocked, timer) : renderUnavailableCard("No step available", "Go back to the recipe and try again.")}

      <div class="footer-actions">
        <div class="footer-actions__row">
          <button class="button button--ghost" type="button" data-action="step-back" ${state.activeStepIndex === 0 ? "disabled" : ""}>Back</button>
          <button class="button button--ghost" type="button" data-action="repeat-step">Repeat step</button>
          <button class="button button--primary" type="button" data-action="step-next">${state.activeStepIndex === recipe.steps.length - 1 ? "Finish recipe" : "Next step"}</button>
        </div>
      </div>
    </section>
  `;
}

function renderStepCard(step, adultHelp, stepBlocked, timer) {
  return `
    <div class="step-card ${stepBlocked ? "step-card--blocked" : adultHelp ? "step-card--help" : ""}">
      <div class="step-card__top">
        <div class="stack stack--tight">
          <div class="badge-line">
            <span class="tag">Step ${escapeHTML(step.order)}</span>
            <span class="tag ${stepBlocked ? "tag--warn" : "tag--soft"}">${escapeHTML(step.safety_level.replace("_", " "))}</span>
          </div>
          <p class="step-text">${escapeHTML(step.instruction)}</p>
        </div>
        <span class="chip ${adultHelp ? "chip--warn" : "chip--accent"}">${adultHelp ? "Adult help" : "Ready"}</span>
      </div>
      ${adultHelp ? `<div class="helper-callout">This step needs an adult before the child continues.</div>` : ""}
      ${step.warnings.length ? `<div class="safety-callout">${escapeHTML(joinList(step.warnings))}</div>` : ""}
      ${step.timers.length ? renderTimerBox(step, timer) : `<div class="state-card"><p class="muted">No timer on this step.</p></div>`}
      ${
        stepBlocked
          ? `<div class="state-card step-card--blocked"><h3>Blocked step</h3><p class="muted">This step is blocked by the current cooking-safety mode. Go back to the recipe or change the mode.</p></div>`
          : ""
      }
    </div>
  `;
}

function renderTimerBox(step, timer) {
  const timerSpec = step.timers[0];
  const active = timer && timer.label === timerSpec.label && !timer.finished;
  const remaining = active ? timer.remaining ?? Math.max(0, Math.ceil((timer.endAt - Date.now()) / 1000)) : timerSpec.duration_seconds;

  return `
    <div class="timer-box">
      <div class="badge-line">
        <span class="chip chip--accent">${escapeHTML(timerSpec.label)}</span>
        <span class="chip chip--quiet">${escapeHTML(formatTimer(timerSpec.duration_seconds))}</span>
      </div>
      <div class="timer-box__time">${escapeHTML(formatTimer(remaining))}</div>
      <p class="timer-box__note">${active ? "Timer running. Keep the step visible." : "Start the timer when the child is ready."}</p>
      <div class="button-row">
        <button class="button button--ghost" type="button" data-action="start-timer" data-label="${escapeHTML(timerSpec.label)}" data-seconds="${escapeHTML(timerSpec.duration_seconds)}" ${active ? "disabled" : ""}>
          ${active ? "Timer running" : "Start timer"}
        </button>
      </div>
    </div>
  `;
}

function renderFavoritesScreen() {
  const favorites = state.recipes.filter((recipe) => state.favorites.includes(recipe.recipe_id));
  return `
    <section class="stack">
      <div class="hero-card">
        <div class="badge-line">
          <span class="chip chip--accent">Favorites</span>
          <span class="chip chip--quiet">${favorites.length} saved</span>
        </div>
        <h2>Saved recipes</h2>
        <p>Favorites are a calm return path. They should stay lightweight and not turn into a ranking system.</p>
        <div class="button-row">
          <button class="button button--ghost" type="button" data-action="route" data-route="meal">Back to meal selection</button>
          <button class="button button--primary" type="button" data-action="route" data-route="suggestions">See suggestions</button>
        </div>
      </div>

      ${favorites.length ? `<div class="favorites-list">${favorites.map((recipe) => renderSuggestionCard(recipe)).join("")}</div>` : renderEmpty("No favorites yet", "Save a recipe after you review it or finish a stepper flow.")}
    </section>
  `;
}

function renderEmpty(title, message) {
  return `
    <div class="empty-card">
      <h3>${escapeHTML(title)}</h3>
      <p class="muted">${escapeHTML(message)}</p>
    </div>
  `;
}

function renderUnavailableCard(title, message) {
  return `
    <div class="state-card step-card--blocked">
      <div class="badge-line">
        <span class="chip chip--warn">Unavailable</span>
        <span class="chip chip--quiet">Local API or selection missing</span>
      </div>
      <h3>${escapeHTML(title)}</h3>
      <p class="muted">${escapeHTML(message)}</p>
    </div>
  `;
}

function renderBusyCard() {
  const total = Math.max(1, state.busyDeadlineAt - state.busyStartedAt);
  const elapsed = Math.max(0, Date.now() - state.busyStartedAt);
  const progress = Math.max(0, Math.min(1, elapsed / total));
  const remainingSeconds = Math.max(0, Math.ceil((state.busyDeadlineAt - Date.now()) / 1000));
  const fillPercent = Math.round(progress * 100);
  const moodClass = state.busyTimedOut ? "cake-loader--sad" : "";
  const statusChip = state.busyTimedOut ? "chip--warn" : "chip--accent";
  const title = state.busyTimedOut ? "Cake flop" : state.busyMessage;
  const detail = state.busyTimedOut
    ? "Local Ollama did not answer before the timer finished. KidsChef will try a smaller fallback."
    : `The cake fills up while KidsChef waits for a local recipe idea. About ${remainingSeconds}s left.`;

  return `
    <div class="state-card busy-card">
      <div class="badge-line">
        <span class="chip ${statusChip}">${state.busyTimedOut ? "Timeout" : "Loading"}</span>
        <span class="chip chip--quiet">${escapeHTML(state.busyMessage)}</span>
      </div>
      <div class="busy-card__body">
        <div class="cake-loader ${moodClass}" aria-hidden="true" style="--cake-fill:${fillPercent}%;">
          <div class="cake-loader__plate"></div>
          <div class="cake-loader__cake">
            <div class="cake-loader__fill"></div>
            <div class="cake-loader__drip cake-loader__drip--one"></div>
            <div class="cake-loader__drip cake-loader__drip--two"></div>
            <div class="cake-loader__face">
              <span class="cake-loader__eye"></span>
              <span class="cake-loader__eye"></span>
              <span class="cake-loader__mouth"></span>
            </div>
          </div>
        </div>
        <div class="stack stack--tight">
          <h3>${escapeHTML(title)}</h3>
          <p class="muted">${escapeHTML(detail)}</p>
          <div class="busy-card__meter" aria-hidden="true">
            <span class="busy-card__meter-fill" style="width:${fillPercent}%;"></span>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderMainContent() {
  if (state.busy) {
    return renderBusyCard();
  }

  switch (state.route) {
    case "meal":
      return renderMealScreen();
    case "ingredients":
      return renderIngredientsScreen();
    case "filters":
      return renderFiltersScreen();
    case "suggestions":
      return renderSuggestionsScreen();
    case "recipe":
      return renderRecipeDetailScreen();
    case "stepper":
      return renderStepperScreen();
    case "favorites":
      return renderFavoritesScreen();
    default:
      return renderMealScreen();
  }
}

function render() {
  const banner = state.apiStatus === "ready" ? "" : renderBanner();

  app.innerHTML = `
    <div class="shell">
      <header class="topbar">
        <div class="brand">
          <div class="brand__mark">KidsChef MVP</div>
          <h1 class="brand__title">${escapeHTML(formatRoute(state.route))}</h1>
          <p class="brand__subtitle">A calm mobile-first cooking flow for kids that talks to local JSON APIs.</p>
        </div>
        ${renderStatusChips()}
      </header>

      <main class="grid stack">
        ${banner}
        ${renderMainContent()}
      </main>
    </div>
  `;
}

function wireEvents() {
  app.addEventListener("click", async (event) => {
    const control = event.target.closest("[data-action]");
    if (!control) return;

    const action = control.dataset.action;

    if (action === "route") {
      goRoute(control.dataset.route);
      return;
    }

    if (action === "choose-meal") {
      setMealType(control.dataset.meal);
      return;
    }

    if (action === "next-from-meal") {
      goNextFromMeal();
      return;
    }

    if (action === "back-from-ingredients") {
      goBackFromIngredients();
      return;
    }

    if (action === "go-filters") {
      state.route = "filters";
      persistState();
      render();
      return;
    }

    if (action === "back-from-filters") {
      goBackFromFilters();
      return;
    }

    if (action === "find-recipes") {
      await findRecipes();
      return;
    }

    if (action === "retry-api") {
      await retryApiConnection();
      return;
    }

    if (action === "open-recipe") {
      await loadRecipeDetail(control.dataset.recipeId, false);
      return;
    }

    if (action === "start-cooking") {
      const recipeId = control.dataset.recipeId;
      const recipe = state.recipes.find((item) => item.recipe_id === recipeId);
      if (!recipe) return;
      const canStart = safetyAllowsRecipe(recipe).allowed && filtersAllowRecipe(recipe).allowed;
      if (!canStart) {
        await loadRecipeDetail(recipeId, false);
        return;
      }
      await loadRecipeDetail(recipeId, true);
      return;
    }

    if (action === "toggle-favorite") {
      await toggleFavorite(control.dataset.recipeId);
      return;
    }

    if (action === "remove-ingredient") {
      removeIngredient(control.dataset.value);
      return;
    }

    if (action === "add-suggested-ingredient") {
      addIngredient(control.dataset.value || "");
      return;
    }

    if (action === "add-all-missing") {
      addIngredient((control.dataset.values || "").replaceAll(",", ", "));
      return;
    }

    if (action === "step-back") {
      stepBackward();
      return;
    }

    if (action === "step-next") {
      stepForward();
      return;
    }

    if (action === "repeat-step") {
      repeatStep();
      return;
    }

    if (action === "start-timer") {
      const seconds = Number(control.dataset.seconds);
      startTimer(seconds, control.dataset.label);
      return;
    }
  });

  app.addEventListener("submit", (event) => {
    const form = event.target.closest("#ingredient-form");
    if (!form) return;
    event.preventDefault();
    const input = form.querySelector("#ingredient-input");
    addIngredient(input.value);
  });

  app.addEventListener("change", (event) => {
    const control = event.target;

    if (control.matches("[data-action='toggle-filter']")) {
      toggleFilter(control.dataset.group, control.dataset.value);
    }
  });

  app.addEventListener("input", (event) => {
    const control = event.target;
    if (control.matches("#ingredient-input")) {
      state.ingredientInput = control.value;
    }
  });

  window.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
      syncTimerFromClock();
      render();
    }
  });
}

function init() {
  wireEvents();
  render();
  bootstrap();
}

init();
