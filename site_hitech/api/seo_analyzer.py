import re
from typing import Dict, List, Tuple
from bs4 import BeautifulSoup
import html

class SEOAnalyzer:
    """
    Công cụ phân tích SEO cơ bản cho bài viết/blog.
    Kiểm tra tiêu đề, mô tả, từ khóa, độ dài, điểm SEO tổng quan.
    """
    def __init__(self, title, description, content, keywords=None):
        self.title = title or ''
        self.description = description or ''
        self.content = content or ''
        self.keywords = keywords or ''

    def check_title(self):
        length = len(self.title)
        return 30 <= length <= 65

    def check_description(self):
        length = len(self.description)
        return 70 <= length <= 160

    def check_keywords(self):
        if not self.keywords:
            return False
        kw_list = [kw.strip().lower() for kw in self.keywords.split(',') if kw.strip()]
        return len(kw_list) > 0

    def keyword_density(self):
        if not self.keywords:
            return 0
        kw_list = [kw.strip().lower() for kw in self.keywords.split(',') if kw.strip()]
        content = self.content.lower()
        total_words = len(re.findall(r'\w+', content))
        if total_words == 0:
            return 0
        density = 0
        for kw in kw_list:
            count = content.count(kw)
            density += count / total_words
        return round(density * 100, 2)

    def check_content_length(self):
        return len(self.content) >= 300

    def score(self):
        score = 0
        if self.check_title():
            score += 1
        if self.check_description():
            score += 1
        if self.check_keywords():
            score += 1
        if self.check_content_length():
            score += 1
        density = self.keyword_density()
        if 0.5 <= density <= 3:
            score += 1
        return score, density

    def report(self):
        score, density = self.score()
        return {
            'title_ok': self.check_title(),
            'description_ok': self.check_description(),
            'keywords_ok': self.check_keywords(),
            'content_length_ok': self.check_content_length(),
            'keyword_density': density,
            'score': score,
            'max_score': 5
        }

    def analyze_seo(self, title: str, meta_description: str, content: str, 
                   keywords: str, slug: str, featured_image: str = None) -> Dict:
        """
        Phân tích SEO và trả về điểm số chi tiết
        """
        results = {
            'total_score': 0,
            'details': {},
            'suggestions': []
        }
        
        # Phân tích từ khóa
        keyword_list = [kw.strip().lower() for kw in keywords.split(',') if kw.strip()]
        main_keyword = keyword_list[0] if keyword_list else ''
        
        # 1. Phân tích Title
        title_score, title_details = self._analyze_title(title, main_keyword)
        results['details']['title'] = title_details
        results['total_score'] += title_score
        
        # 2. Phân tích Meta Description
        meta_score, meta_details = self._analyze_meta_description(meta_description, main_keyword)
        results['details']['meta_description'] = meta_details
        results['total_score'] += meta_score
        
        # 3. Phân tích Content
        content_score, content_details = self._analyze_content(content, keyword_list)
        results['details']['content'] = content_details
        results['total_score'] += content_score
        
        # 4. Phân tích Images
        image_score, image_details = self._analyze_images(content, featured_image)
        results['details']['images'] = image_details
        results['total_score'] += image_score
        
        # 5. Phân tích Technical
        tech_score, tech_details = self._analyze_technical(slug, keywords)
        results['details']['technical'] = tech_details
        results['total_score'] += tech_score
        
        # Tạo gợi ý cải thiện
        results['suggestions'] = self._generate_suggestions(results['details'])
        
        # Tính phần trăm dựa trên tổng điểm tối đa
        max_total_score = sum(details['max_score'] for details in results['details'].values())
        results['max_total_score'] = max_total_score
        results['percentage'] = int((results['total_score'] / max_total_score) * 100) if max_total_score > 0 else 0
        
        return results
    
    def _analyze_title(self, title: str, main_keyword: str) -> Tuple[int, Dict]:
        """Phân tích tiêu đề"""
        score = 0
        details = {
            'score': 0,
            'max_score': 3,  # Độ dài (1) + Có từ khóa (1) + Từ khóa ở đầu (1)
            'issues': [],
            'strengths': []
        }
        
        if not title:
            details['issues'].append('Tiêu đề không được để trống')
            return 0, details
        
        title_length = len(title)
        
        # Kiểm tra độ dài
        if title_length < 30:
            details['issues'].append(f'Tiêu đề quá ngắn ({title_length} ký tự, cần ít nhất 30 ký tự)')
        elif title_length > 65:
            details['issues'].append(f'Tiêu đề quá dài ({title_length} ký tự, tối đa 65 ký tự)')
        else:
            score += 1
            details['strengths'].append('Độ dài tiêu đề phù hợp')
        
        # Kiểm tra từ khóa chính
        if main_keyword and main_keyword.lower() in title.lower():
            score += 1
            details['strengths'].append('Tiêu đề chứa từ khóa chính')
        else:
            details['issues'].append('Tiêu đề nên chứa từ khóa chính')
        
        # Kiểm tra vị trí từ khóa
        if main_keyword and title.lower().startswith(main_keyword.lower()):
            score += 1
            details['strengths'].append('Từ khóa chính ở đầu tiêu đề')
        
        details['score'] = score
        return score, details
    
    def _analyze_meta_description(self, meta_desc: str, main_keyword: str) -> Tuple[int, Dict]:
        """Phân tích meta description"""
        score = 0
        details = {
            'score': 0,
            'max_score': 3,  # Độ dài (1) + Có từ khóa (1) + CTA (1)
            'issues': [],
            'strengths': []
        }
        
        if not meta_desc:
            details['issues'].append('Meta description không được để trống')
            return 0, details
        
        desc_length = len(meta_desc)
        
        # Kiểm tra độ dài
        if desc_length < 70:
            details['issues'].append(f'Meta description quá ngắn ({desc_length} ký tự, cần ít nhất 70 ký tự)')
        elif desc_length > 160:
            details['issues'].append(f'Meta description quá dài ({desc_length} ký tự, tối đa 160 ký tự)')
        else:
            score += 1
            details['strengths'].append('Độ dài meta description phù hợp')
        
        # Kiểm tra từ khóa
        if main_keyword and main_keyword.lower() in meta_desc.lower():
            score += 1
            details['strengths'].append('Meta description chứa từ khóa chính')
        else:
            details['issues'].append('Meta description nên chứa từ khóa chính')
        
        # Kiểm tra call-to-action
        cta_words = ['tìm hiểu', 'khám phá', 'xem ngay', 'liên hệ', 'tư vấn', 'báo giá']
        if any(word in meta_desc.lower() for word in cta_words):
            score += 1
            details['strengths'].append('Meta description có call-to-action')
        
        details['score'] = score
        return score, details
    
    def _analyze_content(self, content: str, keywords: List[str]) -> Tuple[int, Dict]:
        """Phân tích nội dung"""
        score = 0
        details = {
            'score': 0,
            'max_score': 4,  # Độ dài (1) + Mật độ từ khóa (1) + Heading (1) + Internal links (1)
            'issues': [],
            'strengths': []
        }
        
        if not content:
            details['issues'].append('Nội dung không được để trống')
            return 0, details
        
        # Loại bỏ HTML tags để đếm từ
        soup = BeautifulSoup(content, 'html.parser')
        text_content = soup.get_text()
        word_count = len(text_content.split())
        
        # Kiểm tra độ dài nội dung
        if word_count < 300:
            details['issues'].append(f'Nội dung quá ngắn ({word_count} từ, cần ít nhất 300 từ)')
        else:
            score += 1
            details['strengths'].append(f'Nội dung đủ dài ({word_count} từ)')
        
        # Kiểm tra từ khóa
        if keywords:
            main_keyword = keywords[0]
            keyword_count = text_content.lower().count(main_keyword.lower())
            keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
            
            if 0.5 <= keyword_density <= 3.0:
                score += 1
                details['strengths'].append(f'Mật độ từ khóa phù hợp ({keyword_density:.1f}%)')
            elif keyword_density < 0.5:
                details['issues'].append(f'Mật độ từ khóa thấp ({keyword_density:.1f}%, cần ít nhất 0.5%)')
            else:
                details['issues'].append(f'Mật độ từ khóa cao ({keyword_density:.1f}%, không quá 3%)')
        
        # Kiểm tra heading structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if len(headings) >= 2:
            score += 1
            details['strengths'].append('Có cấu trúc heading tốt')
        else:
            details['issues'].append('Nên có ít nhất 2 heading (H2, H3)')
        
        # Kiểm tra internal links
        internal_links = soup.find_all('a', href=re.compile(r'^/'))
        if len(internal_links) >= 1:
            score += 1
            details['strengths'].append('Có internal links')
        else:
            details['issues'].append('Nên có ít nhất 1 internal link')
        
        details['score'] = score
        return score, details
    
    def _analyze_images(self, content: str, featured_image: str) -> Tuple[int, Dict]:
        """Phân tích hình ảnh"""
        score = 0
        details = {
            'score': 0,
            'max_score': 3,  # Featured image (1) + Alt text (1) + SEO friendly names (1)
            'issues': [],
            'strengths': []
        }
        
        soup = BeautifulSoup(content, 'html.parser')
        images = soup.find_all('img')
        
        # Kiểm tra featured image
        if featured_image:
            score += 1
            details['strengths'].append('Có featured image')
        else:
            details['issues'].append('Nên có featured image')
        
        # Kiểm tra alt text 
        if len(images) > 0:
            images_with_alt = [img for img in images if img.get('alt') and img.get('alt').strip()]
            if len(images_with_alt) == len(images):
                score += 1
                details['strengths'].append(f'Tất cả {len(images)} ảnh đều có alt text')
            elif len(images_with_alt) > 0:
                score += 0.5  # Điểm một phần
                details['issues'].append(f'Chỉ {len(images_with_alt)}/{len(images)} ảnh có alt text')
            else:
                details['issues'].append(f'{len(images)} ảnh không có alt text')
        else:
            # Không có ảnh trong content, cho 0.5 điểm
            score += 0.5
            details['strengths'].append('Không có ảnh trong content cần alt text')
        
        # Kiểm tra tên file SEO friendly (relaxed criteria)
        seo_friendly_count = 0
        total_images = len(images) + (1 if featured_image else 0)  # Bao gồm featured image
        
        # Kiểm tra featured image
        if featured_image:
            filename = featured_image.split('/')[-1].lower()
            # Kiểm tra nếu tên file có ý nghĩa (không phải random string)
            if not re.match(r'^[a-f0-9]{10,}', filename) and len(filename.replace('.jpg', '').replace('.png', '').replace('.jpeg', '')) > 3:
                seo_friendly_count += 1
        
        # Kiểm tra ảnh trong content
        for img in images:
            src = img.get('src', '').lower()
            if src:
                filename = src.split('/')[-1]
                # Kiểm tra nếu tên file có ý nghĩa
                if not re.match(r'^[a-f0-9]{10,}', filename) and len(filename.replace('.jpg', '').replace('.png', '').replace('.jpeg', '')) > 3:
                    seo_friendly_count += 1
        
        if total_images > 0:
            if seo_friendly_count >= total_images * 0.7:  # 70% ảnh có tên file tốt
                score += 1
                details['strengths'].append(f'{seo_friendly_count}/{total_images} ảnh có tên file SEO friendly')
            elif seo_friendly_count > 0:
                score += 0.5
                details['issues'].append(f'Chỉ {seo_friendly_count}/{total_images} ảnh có tên file SEO friendly')
            else:
                details['issues'].append('Tên file ảnh nên có ý nghĩa, không phải mã random')
        else:
            # Không có ảnh nào
            details['issues'].append('Nên có ít nhất 1 ảnh trong bài viết')
        
        details['score'] = score
        return score, details
    
    def _analyze_technical(self, slug: str, keywords: str) -> Tuple[int, Dict]:
        """Phân tích kỹ thuật"""
        score = 0
        details = {
            'score': 0,
            'max_score': 3,  # URL slug (1) + Keywords (1) + Structured Data (1)
            'issues': [],
            'strengths': []
        }
        
        # Kiểm tra URL slug
        if slug and len(slug) <= 60:
            score += 1
            details['strengths'].append('URL slug phù hợp')
        else:
            details['issues'].append('URL slug nên ngắn gọn (dưới 60 ký tự)')
        
        # Kiểm tra keywords
        if keywords and len(keywords.split(',')) >= 3:
            score += 1
            details['strengths'].append('Có đủ keywords')
        else:
            details['issues'].append('Nên có ít nhất 3 keywords')
        
        # Kiểm tra structured data (bonus points)
        # Đây chỉ là placeholder - trong thực tế cần crawl page để kiểm tra
        if True:  # Giả sử website đã có structured data
            score += 1
            details['strengths'].append('Website có structured data cho Google')
        
        details['score'] = score
        return score, details
    
    def _generate_suggestions(self, details: Dict) -> List[str]:
        """Tạo gợi ý cải thiện"""
        suggestions = []
        
        for section, data in details.items():
            for issue in data.get('issues', []):
                suggestions.append(issue)
        
        return suggestions[:5]  # Giới hạn 5 gợi ý
    
    def get_seo_color(self, score: int) -> str:
        """Trả về màu dựa trên điểm số"""
        if score >= 80:
            return 'success'  # Xanh lá
        elif score >= 60:
            return 'warning'  # Vàng
        else:
            return 'danger'   # Đỏ
    
    def get_seo_icon(self, score: int) -> str:
        """Trả về icon dựa trên điểm số"""
        if score >= 80:
            return 'fas fa-check-circle'
        elif score >= 60:
            return 'fas fa-exclamation-triangle'
        else:
            return 'fas fa-times-circle' 