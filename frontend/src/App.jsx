import { useEffect, useMemo, useRef, useState } from "react";
import { generateCarousel } from "./api";

const defaultPrompt = "Explain Newton's laws in a fun way for kids and parents...";
const PROMPT_LIMIT = 220;

const formatOptions = [
  { value: "post", label: "Post (1:1)" },
  { value: "story", label: "Story (9:16)" },
  { value: "carousel", label: "Carousel" },
];

const slideCountOptions = [3, 4, 5, 6, 7, 8];

const promptSuggestions = [
  "Create a post explaining the water cycle in a simple way for kids",
  "Make a carousel about why kids forget what they learn and how to fix it",
  "Explain photosynthesis in a fun and easy way for children",
  "Create a story-style post about the solar system for beginners",
  "Make a learning post about fractions using simple examples",
];

const valuePoints = [
  "Makes learning visual and engaging",
  "Helps children understand faster",
  "Helps parents explain concepts easily",
  "Saves time while creating quality content",
];

const steps = [
  "Enter your idea",
  "Choose format (post/story/carousel)",
  "Get ready-to-use content instantly",
];

const faqItems = [
  {
    question: "What does this tool do?",
    answer:
      "It transforms your ideas into visual learning content designed for children.",
  },
  {
    question: "Who is this for?",
    answer: "Students, parents, and educators.",
  },
  {
    question: "How is this different?",
    answer: "It focuses on clarity, simplicity, and engagement.",
  },
  {
    question: "Can I use this for social media?",
    answer: "Yes, all outputs are designed to be ready-to-post.",
  },
];

const navItems = [
  { id: "hero", label: "Home" },
  { id: "studio", label: "Studio" },
  { id: "output", label: "Output" },
  { id: "benefits", label: "Why it helps" },
  { id: "faq", label: "FAQ" },
];

function AccordionItem({ item, isOpen, onToggle }) {
  return (
    <article className={`faq-item ${isOpen ? "open" : ""}`}>
      <button type="button" className="faq-trigger" onClick={onToggle} aria-expanded={isOpen}>
        <span>{item.question}</span>
        <span className="faq-icon">{isOpen ? "-" : "+"}</span>
      </button>
      <div className={`faq-panel ${isOpen ? "open" : ""}`}>
        <p className="faq-answer">{item.answer}</p>
      </div>
    </article>
  );
}

function App() {
  const [prompt, setPrompt] = useState(defaultPrompt);
  const [format, setFormat] = useState("post");
  const [slideCount, setSlideCount] = useState(5);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadedImages, setLoadedImages] = useState({});
  const [openFaqIndex, setOpenFaqIndex] = useState(0);
  const [theme, setTheme] = useState("light");
  const [activeSection, setActiveSection] = useState("hero");
  const [isNavbarScrolled, setIsNavbarScrolled] = useState(false);
  const sectionRefs = useRef([]);

  const previewCount = format === "carousel" ? slideCount : 1;

  useEffect(() => {
    const sections = sectionRefs.current.filter(Boolean);
    if (!sections.length) {
      return undefined;
    }

    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
          }
        });
      },
      { threshold: 0.16 },
    );

    const activeObserver = new IntersectionObserver(
      (entries) => {
        const visibleEntry = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (visibleEntry?.target?.id) {
          setActiveSection(visibleEntry.target.id);
        }
      },
      {
        rootMargin: "-35% 0px -45% 0px",
        threshold: [0.2, 0.35, 0.55],
      },
    );

    sections.forEach((section) => {
      revealObserver.observe(section);
      activeObserver.observe(section);
    });

    return () => {
      revealObserver.disconnect();
      activeObserver.disconnect();
    };
  }, []);

  useEffect(() => {
    function handleScroll() {
      setIsNavbarScrolled(window.scrollY > 50);
    }

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  const sectionHeadingMap = useMemo(
    () => ({
      studio: "Input Studio",
      output: "Output",
      benefits: "Why This Tool",
      "how-it-works": "How It Works",
      faq: "FAQ",
    }),
    [],
  );

  async function handleGenerate() {
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt) {
      setError("Please enter an idea first.");
      return;
    }

    try {
      setIsLoading(true);
      setError("");
      setLoadedImages({});
      const data = await generateCarousel({
        prompt: trimmedPrompt,
        format,
        slide_count: slideCount,
      });
      setResult(data);
    } catch (requestError) {
      const details = requestError.message || "Something went wrong.";
      setError(details);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDownloadImage(imageUrl, title, index) {
    if (!imageUrl) {
      return;
    }

    const filename = `${title || `creative-${index}`}.png`;

    if (imageUrl.startsWith("data:")) {
      const link = document.createElement("a");
      link.href = imageUrl;
      link.download = filename;
      link.click();
      return;
    }

    const response = await fetch(imageUrl);
    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(objectUrl);
  }

  function getCardClassName(activeFormat) {
    return `preview-card preview-${activeFormat}`;
  }

  function toggleTheme() {
    setTheme((current) => (current === "light" ? "dark" : "light"));
  }

  function handlePromptChange(event) {
    setPrompt(event.target.value.slice(0, PROMPT_LIMIT));
  }

  function handleSuggestionClick(suggestion) {
    setPrompt(suggestion.slice(0, PROMPT_LIMIT));
  }

  function setSectionRef(index) {
    return (element) => {
      sectionRefs.current[index] = element;
    };
  }

  return (
    <div className={`app-shell theme-${theme}`}>
      <main className="page-layout">
        <header className={`topbar navbar ${isNavbarScrolled ? "scrolled" : ""}`}>
          <a href="#hero" className="brand-mark">
            <span className="brand-dot" />
            <span className="brand-text">Creative Studio</span>
          </a>

          <nav className="nav-links" aria-label="Page sections">
            {navItems.map((item) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                className={activeSection === item.id ? "active" : ""}
              >
                {item.label}
              </a>
            ))}
          </nav>

          <button type="button" className="theme-toggle" onClick={toggleTheme}>
            {theme === "light" ? "Dark Mode" : "Light Mode"}
          </button>
        </header>

        <section className="hero-section reveal-section is-visible" id="hero" ref={setSectionRef(0)}>
          <div className="hero-copy">
            <span className="eyebrow">Friendly Learning Studio</span>
            <h1>
              Turn Ideas into <span className="accent-text">Beautiful Learning Content</span> for
              Kids
            </h1>
            <p>
              Create engaging posts, stories, and carousels that help children understand
              concepts faster while giving parents clarity and confidence.
            </p>
          </div>
          <div className="hero-card">
            <div className="hero-badge">Made for students, parents, and educators</div>
            <h2>Warm, visual, ready to share</h2>
            <p>
              Start with one rough idea and turn it into a polished learning post that feels easy
              to use and easy to explain.
            </p>
          </div>
        </section>

        <section className="content-section reveal-section" id="studio" ref={setSectionRef(1)}>
          <div className="section-heading">
            <span className="eyebrow">{sectionHeadingMap.studio}</span>
            <h2>Describe the concept you want to teach</h2>
          </div>

          <section className="composer-card">
            <div className="composer-heading">
              <span className="eyebrow">Idea Input</span>
              <h3>Build a post in seconds</h3>
              <p>
                Start with a rough topic and the studio will shape it into a polished social post.
              </p>
            </div>

            <div className="suggestion-row">
              {promptSuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  className="suggestion-chip"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>

            <textarea
              rows="5"
              value={prompt}
              onChange={handlePromptChange}
              placeholder="Explain Newton's laws in a fun way for kids and parents..."
              maxLength={PROMPT_LIMIT}
            />
            <div className="prompt-meta">
              <span className={`char-counter ${prompt.length >= PROMPT_LIMIT ? "limit-reached" : ""}`}>
                {prompt.length} / {PROMPT_LIMIT}
              </span>
              {prompt.length >= PROMPT_LIMIT ? (
                <span className="char-warning">Character limit reached</span>
              ) : null}
            </div>

            <div className="composer-controls">
              <label className="control-field">
                <span>Format</span>
                <div className="select-shell">
                  <select value={format} onChange={(event) => setFormat(event.target.value)}>
                    {formatOptions.map((option) => (
                      <option
                        key={option.value}
                        value={option.value}
                        className={format === option.value ? "is-selected" : ""}
                      >
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </label>

              {format === "carousel" ? (
                <label className="control-field">
                  <span>Slides</span>
                  <div className="select-shell">
                    <select
                      value={slideCount}
                      onChange={(event) => setSlideCount(Number(event.target.value))}
                    >
                      {slideCountOptions.map((count) => (
                        <option key={count} value={count}>
                          {count}
                        </option>
                      ))}
                    </select>
                  </div>
                </label>
              ) : null}

              <button
                type="button"
                className="generate-button"
                onClick={handleGenerate}
                disabled={isLoading}
              >
                {isLoading ? "Generating..." : "Generate"}
              </button>
            </div>
          </section>

          {error ? <p className="error-message">{error}</p> : null}
        </section>

        <section className="content-section reveal-section" id="output" ref={setSectionRef(2)}>
          <div className="section-heading">
            <span className="eyebrow">{sectionHeadingMap.output}</span>
            <h2>See your ready-to-use learning content</h2>
          </div>

          <section className="workspace-section">
            {isLoading ? (
              <div className="loading-state">
                <div className="loading-copy">
                  <span className="eyebrow">In progress</span>
                  <h3>Generating your creative...</h3>
                  <p>
                    We&apos;re writing the concept and building image previews for your selected
                    format.
                  </p>
                </div>

                <div className="preview-grid">
                  {Array.from({ length: previewCount }).map((_, index) => (
                    <article className={getCardClassName(format)} key={index}>
                      <div className="preview-media">
                        <div className="skeleton skeleton-media shimmer" />
                      </div>
                      <div className="preview-body">
                        <div className="skeleton skeleton-line shimmer" />
                        <div className="skeleton skeleton-line short shimmer" />
                        <div className="skeleton skeleton-button shimmer" />
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            ) : result ? (
              <div className="result-shell">
                <article className="prompt-card">
                  <span className="eyebrow">Your idea</span>
                  <p>{result.prompt}</p>
                </article>

                <div className="preview-grid">
                  {result.slides.map((slide) => {
                    const isImageLoaded = Boolean(loadedImages[slide.id]);

                    return (
                      <article className={getCardClassName(result.format)} key={slide.id}>
                        <div className="preview-media">
                          {!isImageLoaded ? <div className="image-placeholder shimmer" /> : null}
                          <img
                            className={`slide-image ${isImageLoaded ? "loaded" : "hidden"}`}
                            src={slide.image_url}
                            alt={slide.title}
                            onLoad={() =>
                              setLoadedImages((current) => ({ ...current, [slide.id]: true }))
                            }
                          />
                        </div>

                        <div className="preview-body">
                          <div className="preview-meta">
                            <span>
                              {result.format === "carousel"
                                ? `Slide ${slide.index}`
                                : result.format === "post"
                                  ? "Instagram Post"
                                  : "Story Preview"}
                            </span>
                          </div>
                          <h3>{slide.title}</h3>
                          <p>{slide.text}</p>
                          <button
                            type="button"
                            className="download-button"
                            onClick={() =>
                              handleDownloadImage(slide.image_url, slide.title, slide.index)
                            }
                          >
                            Download image
                          </button>
                        </div>
                      </article>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <span className="eyebrow">Workspace</span>
                <h3>Generate a creative to see polished social previews here.</h3>
                <p>
                  Pick a format, enter an idea, and the studio will create visual assets you can
                  review and download.
                </p>
              </div>
            )}
          </section>
        </section>

        <section className="content-section reveal-section" id="benefits" ref={setSectionRef(3)}>
          <div className="section-heading">
            <span className="eyebrow">{sectionHeadingMap.benefits}</span>
            <h2>Why this helps students and parents</h2>
          </div>
          <div className="info-grid">
            {valuePoints.map((point) => (
              <article className="info-card" key={point}>
                <div className="info-icon" />
                <p>{point}</p>
              </article>
            ))}
          </div>
        </section>

        <section
          className="content-section reveal-section"
          id="how-it-works"
          ref={setSectionRef(4)}
        >
          <div className="section-heading">
            <span className="eyebrow">How It Works</span>
            <h2>Simple steps from idea to finished content</h2>
          </div>
          <div className="steps-grid">
            {steps.map((step, index) => (
              <article className="step-card" key={step}>
                <span className="step-number">{index + 1}</span>
                <p>{step}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="content-section reveal-section" id="faq" ref={setSectionRef(5)}>
          <div className="section-heading">
            <span className="eyebrow">{sectionHeadingMap.faq}</span>
            <h2>Common questions</h2>
          </div>
          <div className="faq-list">
            {faqItems.map((item, index) => (
              <AccordionItem
                key={item.question}
                item={item}
                isOpen={openFaqIndex === index}
                onToggle={() => setOpenFaqIndex((current) => (current === index ? -1 : index))}
              />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
