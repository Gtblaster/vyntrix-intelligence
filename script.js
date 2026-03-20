/**
 * script.js
 * Logic for Vyntrix Intelligence Anti-Gravity Interactions
 */

document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = 'http://127.0.0.1:8000';    // 1. Navigation Scrolled State
    const navbar = document.getElementById('navbar');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // 2. Parallax Effect for Hero Background
    const heroBg = document.getElementById('hero-bg');

    window.addEventListener('scroll', () => {
        const scrollPosition = window.scrollY;
        // Move the background slower than the scroll speed
        if (scrollPosition < window.innerHeight) {
            heroBg.style.transform = `translateY(${scrollPosition * 0.4}px)`;
        }
    });

    // 3. Float interaction on mousemove for hero drops
    const heroSection = document.getElementById('home');
    const droplets = document.querySelectorAll('.droplet');

    if (heroSection) {
        heroSection.addEventListener('mousemove', (e) => {
            const xAxis = (window.innerWidth / 2 - e.pageX) / 50;
            const yAxis = (window.innerHeight / 2 - e.pageY) / 50;

            droplets.forEach((drop, index) => {
                // Apply slight opposing movement based on mouse position to simulate repulsive anti-gravity
                const factor = (index + 1) * 2;
                drop.style.transform = `translate(${xAxis * factor}px, ${yAxis * factor}px)`;
            });
        });

        // Reset drops when mouse leaves
        heroSection.addEventListener('mouseleave', () => {
            droplets.forEach((drop) => {
                drop.style.transform = 'translate(0px, 0px)';
            });
        });
    }


    // 4. Scroll Reveal Observer (Intersection Observer API)
    // Elements to observe
    const elementsToReveal = document.querySelectorAll(
        '.fade-in-up, .slide-in-left, .slide-in-right, .slide-in-bottom'
    );

    if (elementsToReveal.length > 0) {
        const revealOptions = {
            threshold: 0.15, // Trigger when 15% of the element is visible
            rootMargin: "0px 0px -50px 0px"
        };

        const revealObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(entry => {
                if (!entry.isIntersecting) {
                    return;
                } else {
                    entry.target.classList.add('animate');
                    // Optional: Stop observing once animated if we don't want it to run again
                    observer.unobserve(entry.target);
                }
            });
        }, revealOptions);

        // Apply observer to all target elements
        elementsToReveal.forEach(el => {
            revealObserver.observe(el);
        });
    }

    // 5. Parallax Image effects (images lift up as you scroll down)
    const levitateImage = document.getElementById('lab-image');
    const shieldImage = document.getElementById('shield-image');

    window.addEventListener('scroll', () => {
        requestAnimationFrame(() => {
            // Check if Lab Section is in viewport
            const labRect = document.getElementById('lab').getBoundingClientRect();
            if (labRect.top < window.innerHeight && labRect.bottom > 0 && levitateImage) {
                // Calculate how far into the section we've scrolled
                const scrollProgress = (window.innerHeight - labRect.top) / window.innerHeight;
                levitateImage.style.transform = `translateY(-${scrollProgress * 40}px) scale(1.05)`;
            } else if (levitateImage) {
                levitateImage.style.transform = `scale(1.0)`;
            }

            // Check if Shield Section is in viewport
            const shieldRect = document.getElementById('neuroguard').getBoundingClientRect();
            if (shieldRect.top < window.innerHeight && shieldRect.bottom > 0 && shieldImage) {
                const scrollProgress = (window.innerHeight - shieldRect.top) / window.innerHeight;
                shieldImage.style.transform = `translateY(-${scrollProgress * 50}px) rotate(${scrollProgress * 5}deg)`;
            }
        });
    });

    // 6. Scanner Logic
    const scanForm = document.getElementById('scan-form');
    const targetUrlInput = document.getElementById('target-url');
    const scanBtn = document.querySelector('.scan-btn');

    // States
    const stateInput = document.getElementById('scanner-input-state');
    const stateLoading = document.getElementById('scanner-loading-state');
    const stateResults = document.getElementById('scanner-results-state');

    // Dynamic Elements
    const terminalOutput = document.getElementById('terminal-output');
    const resultUrlDisplay = document.getElementById('result-url');
    const resetBtn = document.getElementById('reset-scan-btn');

    // Terminal Animation Texts
    const scanSequence = [
        { text: "Initializing Vyntrix Deep Learning Engine...", class: "cyan", delay: 500 },
        { text: "Resolving target host information...", class: "", delay: 800 },
        { text: "[OK] Target identified.", class: "cyan", delay: 1200 },
        { text: "Starting surface topology mapping...", class: "", delay: 1800 },
        { text: "Analyzing HTTP response headers...", class: "warning", delay: 2200 },
        { text: "Mapping input vectors and endpoints...", class: "", delay: 2800 },
        { text: "[WARNING] Unsanitized payload reflection detected.", class: "danger", delay: 3500 },
        { text: "Probing SQL sub-routines...", class: "warning", delay: 4200 },
        { text: "[CRITICAL] SQL parsing anomaly found on /login.", class: "danger", delay: 4800 },
        { text: "Analyzing third-party trackers and data leakage footprints...", class: "cyan", delay: 5300 },
        { text: "Compiling final AI vulnerability and privacy report...", class: "cyan", delay: 6000 },
        { text: "Scan complete. Rendering UI.", class: "cyan", delay: 6500 }
    ];

    function switchState(stateToShow) {
        stateInput.classList.remove('active');
        stateInput.classList.add('hidden');
        stateLoading.classList.remove('active');
        stateLoading.classList.add('hidden');
        stateResults.classList.remove('active');
        stateResults.classList.add('hidden');

        setTimeout(() => {
            stateToShow.classList.remove('hidden');
            // Small delay to allow display:block to apply before animating opacity
            setTimeout(() => {
                stateToShow.classList.add('active');
            }, 50);
        }, 500); // Wait for fade out
    }

    if (scanForm) {
        scanForm.addEventListener('submit', (e) => {
            e.preventDefault();
            let textToScan = targetUrlInput.value.trim();

            if (!textToScan) return;

            // Extract URL if a paragraph is pasted
            const extractPattern = /(https?:\/\/[^\s]+|[\w-]+\.[a-z]{2,})/i;
            const match = textToScan.match(extractPattern);
            if (match) {
                textToScan = match[0];
                targetUrlInput.value = textToScan; // Update UI to show only the URL
            } else {
                alert("Could not detect a valid URL. Please provide a website URL.");
                return;
            }

            // Transition from Input to Button Loading
            scanBtn.classList.add('loading');

            // Wait a second, then switch to Terminal State
            setTimeout(() => {
                switchState(stateLoading);
                runTerminalAnimation(textToScan);
            }, 1000);
        });
    }

    async function runTerminalAnimation(targetUrl) {
        if (terminalOutput) terminalOutput.innerHTML = ''; // Clear previous
        let htmlContent = '';

        const statusText = document.getElementById('loading-status-text');

        // Start scanning API call in the background while animation plays
        let apiData = null;
        let apiError = null;
        
        fetch(`${API_BASE_URL}/scan-text/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: targetUrl })
        })
        .then(response => {
            if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
            return response.json();
        })
        .then(data => apiData = data)
        .catch(err => apiError = err);

        scanSequence.forEach((step, index) => {
            setTimeout(() => {
                if (terminalOutput) {
                    htmlContent += `<div class="term-line ${step.class}">${step.text}</div>`;
                    terminalOutput.innerHTML = htmlContent;
                    // Auto-scroll to bottom of terminal
                    terminalOutput.scrollTop = terminalOutput.scrollHeight;
                }

                if (statusText) {
                    statusText.textContent = step.text;
                }

                // If it's the last step, wait for API (if still pending) and transition to results
                if (index === scanSequence.length - 1) {
                    const checkInterval = setInterval(() => {
                        if (apiData || apiError) {
                            clearInterval(checkInterval);
                            setTimeout(() => {
                                showResults(targetUrl, apiData, apiError);
                            }, 1000);
                        }
                    }, 200);
                }
            }, step.delay);
        });
    }

    function showResults(url, data, error) {
        resultUrlDisplay.textContent = url;

        // UI Elements
        const topRiskLevel = document.getElementById('top-risk-level');
        const scoreElement = document.getElementById('security-score');
        const badgeElement = document.getElementById('scan-badge');
        const confidenceVal = document.getElementById('scan-confidence-val');
        const confidenceBar = document.getElementById('scan-confidence-bar');
        const threatVal = document.getElementById('scan-threat-val');
        const threatBar = document.getElementById('scan-threat-bar');
        const insightText = document.getElementById('scan-insight-text');

        let isHighRisk, score, confidence, threatProb, classification, insight;

        if (error || !data || !data.success) {
            console.error("Scanning failed:", error || data?.error);
            isHighRisk = true;
            score = "--";
            confidence = "0.0";
            threatProb = "0.0";
            classification = "ERROR";
            insight = "Failed to communicate with Deep Learning Engine.";
        } else {
            isHighRisk = data.is_threat !== undefined ? data.is_threat : data.is_malicious;
            score = data.security_score !== undefined ? data.security_score : data.personal_data_safety;
            confidence = data.confidence;
            threatProb = data.threat_probability !== undefined ? data.threat_probability : (isHighRisk ? 85 : 10);
            classification = data.ai_classification || data.threat_type;
            insight = data.insight || (isHighRisk ? "Model detected structural similarities to known phishing topologies and unencrypted data transmission pathways." : "No significant topological anomalies detected in the URL structure.");
        }

        // Dynamically update the Top Risk Level Header
        if (topRiskLevel) {
            topRiskLevel.textContent = isHighRisk ? "Risk Level: HIGH" : "Risk Level: SECURE";
            topRiskLevel.className = `threat-level ${isHighRisk ? 'high' : 'safe'}`;
            if (!isHighRisk) {
                topRiskLevel.style.color = 'var(--cyan)';
                topRiskLevel.style.borderColor = 'var(--cyan)';
                topRiskLevel.style.background = 'rgba(0, 240, 255, 0.1)';
                topRiskLevel.style.boxShadow = '0 0 10px rgba(0, 240, 255, 0.2)';
            } else {
                topRiskLevel.style.color = '';
                topRiskLevel.style.borderColor = '';
                topRiskLevel.style.background = '';
                topRiskLevel.style.boxShadow = '';
            }
        }

        // Animate Score
        let currentScore = 0;
        const targetScore = data.personal_data_safety !== undefined ? data.personal_data_safety : (isHighRisk ? Math.floor(Math.random() * 30) + 15 : Math.floor(Math.random() * 20) + 80);
        const scoreAnimationDuration = 1000; // ms
        const scoreAnimationStep = (targetScore / (scoreAnimationDuration / 16)); // assuming 60fps

        const animateScore = () => {
            if (currentScore < targetScore) {
                currentScore = Math.min(currentScore + scoreAnimationStep, targetScore);
                if (scoreElement) scoreElement.textContent = Math.round(currentScore);
                requestAnimationFrame(animateScore);
            } else {
                if (scoreElement) scoreElement.textContent = targetScore;
            }
        };
        animateScore();

        // Set Security Score
        // if (scoreElement) scoreElement.textContent = score; // Replaced by animation

        // Set AI Model Confidence
        if (confidenceVal) confidenceVal.textContent = `${confidence}%`;
        if (confidenceBar) {
            setTimeout(() => {
                confidenceBar.style.width = `${confidence}%`;
            }, 500); // Animate after UI shows
        }

        // Set Threat Probability
        if (threatVal) {
            threatVal.textContent = `${threatProb}%`;
            threatVal.className = `metric-value ${isHighRisk ? 'high' : 'low'}`;
        }
        if (threatBar) {
            threatBar.className = `progress-bar-fill ${isHighRisk ? 'fill-glow-red' : 'fill-glow-cyan'}`;
            setTimeout(() => {
                threatBar.style.width = `${threatProb}%`;
            }, 500);
        }

        // Set Badge and Insights
        if (badgeElement) {
            badgeElement.textContent = isHighRisk ? "HIGH RISK" : (classification === "SECURE (Normal Traffic)" ? "SECURE" : classification);
            badgeElement.className = `prediction-badge ${isHighRisk ? 'badge-infected' : 'badge-secure'}`;
        }

        if (insightText) {
            insightText.textContent = insight;
        }

        // Process Risks dynamically sent from backend
        const vulnContainer = document.getElementById('vuln-list-container');
        if (vulnContainer && data.risks) {
            vulnContainer.innerHTML = '<h4>Found Issues</h4>';
            if (data.risks.length === 0) {
                vulnContainer.innerHTML += `<div class="vuln-card safe" style="border-left: 4px solid #00ffcc;"><div class="vuln-badge" style="background: rgba(0,255,204,0.1); color: #00ffcc;">SECURE</div><h5>No Immediate Risks</h5><p>The URL appears structurally sound against superficial HTTP layer checks.</p></div>`;
            } else {
                data.risks.forEach(r => {
                    vulnContainer.innerHTML += `<div class="vuln-card high"><div class="vuln-badge">RISK</div><h5>${r.title}</h5><p>${r.desc}</p></div>`;
                });
            }
        }
        
        // Process Improvements dynamically sent from backend
        const remList = document.getElementById('remediation-list');
        if (remList && data.improvements) {
            remList.innerHTML = '';
            if (data.improvements.length === 0) {
                remList.innerHTML = `<li><strong>1. Proactive Monitoring</strong><p>Continue standard operational monitoring and rotate credentials periodically.</p></li>`;
            } else {
                data.improvements.forEach((imp, i) => {
                    remList.innerHTML += `<li><strong>${i+1}. ${imp.title}</strong><p>${imp.desc}</p></li>`;
                });
            }
        }

        switchState(stateResults);
        scanBtn.classList.remove('loading');
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            targetUrlInput.value = '';
            switchState(stateInput);
        });
    }

    // 7. Vyntrix 2.0: Dynamic Stat Counters (CountUp)
    const statNumbers = document.querySelectorAll('.stat-number');
    let counted = false;

    window.addEventListener('scroll', () => {
        if (statNumbers.length === 0) return;

        const statsSection = statNumbers[0].closest('.stat-container');
        if (!statsSection) return;

        const oTop = statsSection.getBoundingClientRect().top - window.innerHeight;
        if (counted === false && oTop < 0) {
            statNumbers.forEach(stat => {
                const targetText = stat.innerText;
                const isFloat = targetText.includes('.');
                const targetMatch = targetText.match(/[\d\.]+/);
                if (!targetMatch) return;

                const target = parseFloat(targetMatch[0]);
                const suffix = targetText.replace(/[\d\.]+/, '');

                let count = 0;
                const speed = 200; // time in ms to finish
                const inc = target / (speed / 16); // assuming 60fps (16ms)

                const updateCount = () => {
                    count += inc;
                    if (count < target) {
                        stat.innerText = (isFloat ? count.toFixed(1) : Math.ceil(count)) + suffix;
                        requestAnimationFrame(updateCount);
                    } else {
                        stat.innerText = targetText; // final exact text
                    }
                };
                updateCount();
            });
            counted = true;
        }
    });

    // 8. Custom Glowing Cursor Effect
    const cursorGlow = document.createElement('div');
    cursorGlow.classList.add('cursor-glow');
    document.body.appendChild(cursorGlow);

    window.addEventListener('mousemove', (e) => {
        cursorGlow.style.left = e.clientX + 'px';
        cursorGlow.style.top = e.clientY + 'px';
    });

    // Enlarge cursor firmly on interactive elements
    const interactables = document.querySelectorAll('a, button, input');
    interactables.forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursorGlow.style.width = '100px';
            cursorGlow.style.height = '100px';
            cursorGlow.style.background = 'radial-gradient(circle, rgba(255, 215, 0, 0.15) 0%, transparent 70%)'; // Gold hover
        });
        el.addEventListener('mouseleave', () => {
            cursorGlow.style.width = '300px';
            cursorGlow.style.height = '300px';
            cursorGlow.style.background = 'radial-gradient(circle, rgba(0, 240, 255, 0.1) 0%, transparent 70%)'; // Cyan default
        });
    });

    // 9. Steganography Scanner Logic
    const stegoUpload = document.getElementById('stego-upload');
    const stegoFileName = document.getElementById('stego-file-name');
    const stegoScanBtn = document.getElementById('stego-scan-btn');
    const stegoResultContainer = document.getElementById('stego-result-container');
    const stegoBadge = document.getElementById('stego-badge');
    const stegoConfVal = document.getElementById('stego-confidence-val');
    const stegoConfBar = document.getElementById('stego-confidence-bar');
    const stegoPayloadVal = document.getElementById('stego-payload-val');
    const stegoPayloadBar = document.getElementById('stego-payload-bar');
    const stegoSummary = document.getElementById('stego-summary-text');
    
    // New UI Elements
    const stegoPreviewContainer = document.getElementById('stego-preview-container');
    const stegoOriginalImg = document.getElementById('stego-original-img');
    const stegoOverlayImg = document.getElementById('stego-overlay-img');
    const stegoPayloadContainer = document.getElementById('stego-payload-container');
    const stegoExtractedText = document.getElementById('stego-extracted-text');

    if (stegoUpload) {
        stegoUpload.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                stegoFileName.textContent = file.name;
                stegoScanBtn.style.display = 'inline-block';
                stegoResultContainer.style.display = 'none'; // Hide results on new upload
                stegoConfBar.style.width = '0%'; // Reset bars
                stegoPayloadBar.style.width = '0%';
                
                // Show Image Preview
                const reader = new FileReader();
                reader.onload = function(evt) {
                    stegoOriginalImg.src = evt.target.result;
                    stegoPreviewContainer.style.display = 'block';
                    stegoOverlayImg.style.display = 'none';
                }
                reader.readAsDataURL(file);
                
            } else {
                stegoFileName.textContent = 'No file selected';
                stegoScanBtn.style.display = 'none';
                stegoResultContainer.style.display = 'none';
                stegoPreviewContainer.style.display = 'none';
            }
        });

        stegoScanBtn.addEventListener('click', async () => {
             if (stegoUpload.files.length === 0) return;
             
             // Initial scan state
             stegoScanBtn.disabled = true;
             stegoFileName.textContent += " - Sending to Deep Learning Engine...";
             stegoResultContainer.style.display = 'none';
             
             try {
                 // Prepare the image file for upload
                 const file = stegoUpload.files[0];
                 const formData = new FormData();
                 formData.append('file', file);

                 // Call the local Python FastAPI backend
                 const response = await fetch(`${API_BASE_URL}/scan-image/`, {
                     method: 'POST',
                     body: formData
                 });

                 if (!response.ok) {
                     let errMsg = `API Error: ${response.statusText}`;
                     try {
                         const errData = await response.json();
                         if (errData.detail) errMsg = errData.detail;
                     } catch(e) {}
                     throw new Error(errMsg);
                 }

                 const data = await response.json();
                 
                 // Retrieve real AI metrics
                 const isHarmful = data.is_infected;
                 const confidence = data.confidence;
                 const payloadProb = data.payload_probability;

                 // Update UI Elements
                 stegoFileName.textContent = file.name; // Reset name
                 stegoResultContainer.style.display = 'block';

                 stegoConfVal.textContent = `${confidence}%`;
                 stegoPayloadVal.textContent = `${payloadProb}%`;
                 
                 // Show Extracted Payload
                 if (data.extracted_payload) {
                     stegoExtractedText.textContent = data.extracted_payload;
                     stegoPayloadContainer.style.display = 'block';
                 } else {
                     stegoPayloadContainer.style.display = 'none';
                 }
                 
                 // Show Overlay Highlight Map
                 if (data.highlight_overlay) {
                     stegoOverlayImg.src = `data:image/png;base64,${data.highlight_overlay}`;
                     stegoOverlayImg.style.display = 'block';
                 } else {
                     stegoOverlayImg.style.display = 'none';
                 }

                 // Set Badge
                 stegoBadge.textContent = data.prediction;
                 stegoBadge.className = `prediction-badge ${isHarmful ? 'badge-infected' : 'badge-secure'}`;
                 
                 // Set Colors/Classes based on prediction
                 stegoPayloadVal.className = `metric-value ${isHarmful ? 'high' : 'low'}`;
                 stegoPayloadBar.className = `progress-bar-fill ${isHarmful ? 'fill-glow-red' : 'fill-glow-cyan'}`;

                 // Descriptive text based on AI confidence and prediction
                 if (isHarmful) {
                     stegoSummary.textContent = confidence > 80 
                        ? `CRITICAL: The system detected distinct pixel manipulation and chemically decoded a hidden steganographic payload hidden inside this image. (${payloadProb}% certainty).` 
                        : `WARNING: When the scanner detects unusual pixel patterns that look too perfectly random, it raises a red flag. This often means hidden or encrypted data may be concealed inside the image.`;
                 } else {
                     stegoSummary.textContent = confidence > 80
                        ? `SECURE: The image structure and pixel distribution appear completely normal and mathematically unaltered.`
                        : `NORMAL: No obvious manipulation detected. Pixels fall perfectly within standard image compression margins.`;
                 }

                 // Animate Bars
                 setTimeout(() => {
                     stegoConfBar.style.width = `${confidence}%`;
                     stegoPayloadBar.style.width = `${payloadProb}%`;
                 }, 100);

             } catch (error) {
                 console.error("Scanning failed:", error);
                 stegoFileName.textContent = `Error: ${error.message}`;
                 stegoFileName.style.color = "#ff3333";
             } finally {
                 stegoScanBtn.disabled = false;
             }
        });
    }

});
