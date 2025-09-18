class PageTranslator {
    constructor() {
        this.currentLang = 'vi';
        this.translateUrl = '/api/translate/';
        this.translatePageUrl = '/api/translate-page/';
        this.init();
    }
    
    init() {
        // Khởi tạo dropdown
        this.initLanguageDropdown();
    }
    
    initLanguageDropdown() {
        const dropdownToggle = document.querySelector('.language-dropdown-toggle');
        const dropdownMenu = document.querySelector('.language-dropdown-menu');
        
        if (dropdownToggle && dropdownMenu) {
            dropdownToggle.addEventListener('click', (e) => {
                e.preventDefault();
                dropdownMenu.classList.toggle('show');
                dropdownToggle.classList.toggle('active');
            });
            
            // Đóng dropdown khi click bên ngoài
            document.addEventListener('click', (e) => {
                if (!dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                    dropdownMenu.classList.remove('show');
                    dropdownToggle.classList.remove('active');
                }
            });
            
            // Lắng nghe click trên các option
            document.querySelectorAll('.language-option').forEach(option => {
                option.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetLang = option.getAttribute('data-lang');
                    this.translatePage(targetLang);
                    dropdownMenu.classList.remove('show');
                    dropdownToggle.classList.remove('active');
                });
            });
        }
    }
    
    async translatePage(targetLang) {
        if (targetLang === this.currentLang) return;
        
        // Hiển thị loading
        this.showLoading();
        
        try {
            // Lấy tất cả text elements
            const textElements = this.getTextElements();
            
            // Gọi API dịch
            const response = await fetch(this.translatePageUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    text_elements: textElements,
                    source_lang: this.currentLang,
                    target_lang: targetLang
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Áp dụng bản dịch
                this.applyTranslations(result.translated_elements);
                this.currentLang = targetLang;
                this.updateLanguageDropdown(targetLang);
            } else {
                console.error('Translation failed:', result.error);
                this.showError('Dịch thuật thất bại: ' + result.error);
            }
        } catch (error) {
            console.error('Translation error:', error);
            this.showError('Lỗi kết nối dịch thuật');
        } finally {
            this.hideLoading();
        }
    }
    
    getTextElements() {
        const elements = [];
        const selectors = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'span', 'div', 'a', 'button', 'label',
            'input[placeholder]', 'textarea[placeholder]',
            '.card-title', '.card-text', '.btn-text',
            '.nav-link', '.navbar-brand'
        ];
        
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach((element, index) => {
                const text = element.textContent?.trim() || element.placeholder?.trim();
                if (text && text.length > 0 && !element.querySelector('img')) {
                    elements.push({
                        selector: selector,
                        text: text,
                        index: index
                    });
                }
            });
        });
        
        return elements;
    }
    
    applyTranslations(translatedElements) {
        translatedElements.forEach(item => {
            const elements = document.querySelectorAll(item.selector);
            if (elements[item.index]) {
                elements[item.index].textContent = item.translated_text;
            }
        });
    }
    
    updateLanguageDropdown(lang) {
        const dropdownToggle = document.querySelector('.language-dropdown-toggle');
        if (dropdownToggle) {
            const flagIcon = dropdownToggle.querySelector('.flag-icon');
            const langText = dropdownToggle.querySelector('.lang-text');
            
            const languages = {
                'vi': { flag: '/static/images/flags/vietnam.svg', name: 'Tiếng Việt', code: 'VI' },
                'en': { flag: '/static/images/flags/usa.svg', name: 'English', code: 'EN' },
                'zh': { flag: '/static/images/flags/china.svg', name: '中文', code: 'ZH' },
                'ja': { flag: '/static/images/flags/japan.svg', name: '日本語', code: 'JA' }
            };
            
            if (languages[lang]) {
                flagIcon.src = languages[lang].flag;
                langText.textContent = languages[lang].code;
            }
        }
    }
    
    showLoading() {
        // Tạo loading indicator
        const loading = document.createElement('div');
        loading.id = 'translation-loading';
        loading.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="sr-only">Đang dịch...</span></div>';
        loading.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 9999; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);';
        document.body.appendChild(loading);
    }
    
    hideLoading() {
        const loading = document.getElementById('translation-loading');
        if (loading) {
            loading.remove();
        }
    }
    
    showError(message) {
        // Hiển thị thông báo lỗi
        const error = document.createElement('div');
        error.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        error.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        document.body.appendChild(error);
        
        setTimeout(() => error.remove(), 3000);
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    }
}

// Khởi tạo translator khi trang load
document.addEventListener('DOMContentLoaded', () => {
    new PageTranslator();
}); 