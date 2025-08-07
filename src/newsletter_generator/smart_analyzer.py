"""
Smart Content Quality Analyzer using NLP

This module uses Natural Language Processing techniques to:
1. Assess content quality automatically
2. Classify articles into meaningful categories using Enhanced Semantic Classification
3. Extract key information and entities
4. Determine relevance and newsworthiness
"""

import re
import string
from collections import Counter
from datetime import datetime, timedelta

# Enhanced NLP Classification imports (optional Zero-Shot fallback)
try:
    from transformers import pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
    print("Enhanced NLP available (Zero-Shot as fallback)")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("📝 Using Enhanced Keyword-Based Classification")

# Basic NLP functionality - works without external libraries
class SmartContentAnalyzer:
    """
    Advanced content analysis using Enhanced Semantic Classification
    """
    
    def __init__(self):
        # Zero-Shot classifier (optional enhancement)
        self.zero_shot_classifier = None
        self.use_zero_shot = False
        
        # Attempt to load Zero-Shot classifier
        if TRANSFORMERS_AVAILABLE:
            try:
                print("Loading Zero-Shot Classification model (DistilBERT)...")
                self.zero_shot_classifier = pipeline(
                    "zero-shot-classification",
                    model="typeform/distilbert-base-uncased-mnli",  # Smaller model ~250MB
                    device=-1  # Use CPU
                )
                self.use_zero_shot = True
                print("Zero-Shot Classification enabled")
            except Exception as e:
                print(f"Zero-Shot unavailable: {str(e)[:100]}...")
                print("   Falling back to enhanced keyword classification")
                self.zero_shot_classifier = None
                self.use_zero_shot = False
        
        # Enhanced semantic keyword categories with context and weights
        self.enhanced_categories = {
            'local_government': {
                'primary_keywords': [
                    'council', 'mayor', 'city', 'municipal', 'government', 'policy', 
                    'budget', 'bylaw', 'meeting', 'vote', 'elected', 'official'
                ],
                'context_keywords': [
                    'administration', 'committee', 'planning', 'zoning', 'permits',
                    'tax', 'public works', 'infrastructure', 'spending', 'approval'
                ],
                'title_boosters': ['council', 'mayor', 'city', 'municipal'],
                'weight': 1.2
            },
            'community_events': {
                'primary_keywords': [
                    'festival', 'event', 'celebration', 'community', 'residents',
                    'gathering', 'volunteer', 'fundraiser', 'parade', 'concert'
                ],
                'context_keywords': [
                    'neighborhood', 'local', 'cultural', 'arts', 'music', 'theater', 
                    'library', 'recreation', 'activities', 'family'
                ],
                'title_boosters': ['festival', 'event', 'celebration'],
                'weight': 1.0
            },
            'business_economy': {
                'primary_keywords': [
                    'business', 'company', 'economic', 'jobs', 'employment', 
                    'development', 'investment', 'construction', 'retail',
                    'strike', 'labor', 'union', 'workers', 'negotiations'
                ],
                'context_keywords': [
                    'commerce', 'industry', 'manufacturing', 'startup', 'entrepreneur', 
                    'market', 'growth', 'expansion', 'opening', 'closing',
                    'contract', 'wages', 'working conditions', 'collective bargaining'
                ],
                'title_boosters': ['business', 'company', 'jobs', 'strike', 'workers'],
                'weight': 1.1
            },
            'public_safety': {
                'primary_keywords': [
                    'police', 'fire', 'emergency', 'accident', 'crime', 'safety',
                    'rescue', 'ambulance', 'investigation', 'arrest', 'intruder',
                    'break in', 'robbery', 'assault', 'theft', 'burglary'
                ],
                'context_keywords': [
                    'hospital', 'medical', 'health', 'court', 'legal', 'lawsuit',
                    'fraud', 'traffic', 'security', 'danger', 'victim',
                    'criminal', 'suspicious', 'threatening'
                ],
                'title_boosters': ['police', 'fire', 'emergency', 'accident', 'crime', 'intruder'],
                'weight': 1.3
            },
            'environment_weather': {
                'primary_keywords': [
                    'weather', 'storm', 'rain', 'snow', 'temperature', 'climate',
                    'environment', 'pollution', 'conservation', 'wildlife'
                ],
                'context_keywords': [
                    'nature', 'park', 'forest', 'lake', 'river', 'air quality', 
                    'water', 'recycling', 'sustainability', 'green', 'renewable'
                ],
                'title_boosters': ['weather', 'storm', 'environment'],
                'weight': 1.0
            },
            'education': {
                'primary_keywords': [
                    'school', 'university', 'college', 'student', 'teacher', 'education',
                    'learning', 'graduation', 'academic', 'research'
                ],
                'context_keywords': [
                    'study', 'enrollment', 'curriculum', 'classroom', 'principal', 
                    'board', 'exam', 'degree', 'scholarship'
                ],
                'title_boosters': ['school', 'university', 'student'],
                'weight': 1.0
            },
            'health': {
                'primary_keywords': [
                    'health', 'medical', 'hospital', 'doctor', 'patient', 'treatment',
                    'disease', 'illness', 'healthcare', 'clinic'
                ],
                'context_keywords': [
                    'medicine', 'outbreak', 'vaccine', 'public health', 'mental health', 
                    'therapy', 'surgery', 'diagnosis', 'recovery'
                ],
                'title_boosters': ['health', 'medical', 'hospital'],
                'weight': 1.1
            },
            'sports': {
                'primary_keywords': [
                    'hockey', 'football', 'baseball', 'basketball', 'soccer', 'tennis',
                    'golf', 'swimming', 'skating', 'team', 'player', 'coach'
                ],
                'context_keywords': [
                    'championship', 'tournament', 'league', 'game', 'match', 'sport',
                    'athlete', 'training', 'competition', 'victory'
                ],
                'title_boosters': ['hockey', 'football', 'team'],
                'weight': 1.0
            }
        }
        
        # Legacy categories for backward compatibility
        self.news_categories = {
            cat: data['primary_keywords'] + data['context_keywords'] 
            for cat, data in self.enhanced_categories.items()
        }
        # News categories and their keywords
        self.news_categories = {
            'local_government': [
                'council', 'mayor', 'city', 'municipal', 'government', 'policy', 
                'budget', 'bylaw', 'meeting', 'vote', 'elected', 'official',
                'administration', 'committee', 'planning', 'zoning', 'permits'
            ],
            'community_events': [
                'festival', 'event', 'celebration', 'community', 'residents',
                'neighborhood', 'local', 'gathering', 'volunteer', 'fundraiser',
                'parade', 'concert', 'sports', 'recreation', 'activities',
                'cultural', 'arts', 'music', 'theater', 'library'
            ],
            'business_economy': [
                'business', 'company', 'economic', 'jobs', 'employment', 
                'development', 'investment', 'construction', 'retail', 'commerce',
                'industry', 'manufacturing', 'startup', 'entrepreneur', 'market',
                'growth', 'expansion', 'opening', 'closing', 'bankruptcy'
            ],
            'public_safety': [
                'police', 'fire', 'emergency', 'accident', 'crime', 'safety',
                'rescue', 'ambulance', 'hospital', 'medical', 'health',
                'investigation', 'arrest', 'court', 'legal', 'lawsuit',
                'theft', 'robbery', 'assault', 'fraud', 'traffic'
            ],
            'environment_weather': [
                'weather', 'storm', 'rain', 'snow', 'temperature', 'climate',
                'environment', 'pollution', 'conservation', 'wildlife', 'nature',
                'park', 'forest', 'lake', 'river', 'air quality', 'water',
                'recycling', 'sustainability', 'green', 'renewable'
            ],
            'education': [
                'school', 'university', 'college', 'student', 'teacher', 'education',
                'learning', 'graduation', 'academic', 'research', 'study',
                'enrollment', 'curriculum', 'classroom', 'principal', 'board'
            ],
            'health': [
                'health', 'medical', 'hospital', 'doctor', 'patient', 'treatment',
                'disease', 'illness', 'healthcare', 'clinic', 'medicine',
                'outbreak', 'vaccine', 'public health', 'mental health', 'therapy'
            ],
            'sports': [
                'hockey', 'football', 'baseball', 'basketball', 'soccer', 'tennis',
                'golf', 'swimming', 'skating', 'team', 'player', 'coach',
                'championship', 'tournament', 'league', 'game', 'match', 'sport'
            ]
        }
        
        # Quality indicators - signs of good journalism
        self.quality_indicators = {
            'journalistic': [
                'reported', 'announced', 'according to', 'sources', 'officials',
                'spokesperson', 'statement', 'confirmed', 'investigation', 'interview',
                'witnesses', 'experts', 'analysis', 'background', 'context'
            ],
            'temporal': [
                'today', 'yesterday', 'this week', 'last month', 'recently',
                'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                'saturday', 'sunday', 'january', 'february', 'march', 'april',
                'may', 'june', 'july', 'august', 'september', 'october',
                'november', 'december', '2024', '2025'
            ],
            'factual': [
                'data', 'statistics', 'numbers', 'percent', 'increased', 'decreased',
                'study', 'research', 'survey', 'report', 'findings', 'results',
                'evidence', 'facts', 'figures', 'analysis', 'comparison'
            ]
        }
        
        # Junk content indicators - signs of non-news content
        self.junk_indicators = [
            # Navigation and UI elements
            'click here', 'read more', 'view all', 'show more', 'load more',
            'subscribe', 'newsletter', 'follow us', 'social media', 'share',
            'advertisement', 'sponsored', 'promoted', 'affiliate',
            
            # Legal/footer content
            'terms of service', 'privacy policy', 'cookie policy', 'disclaimer',
            'copyright', 'all rights reserved', 'contact us', 'about us',
            
            # Technical junk
            'lorem ipsum', 'placeholder', 'test content', 'javascript',
            'error', '404', 'page not found', 'loading', 'search results'
        ]
        
    def analyze_content_quality(self, article):
        """
        Analyze the quality of an article using NLP techniques
        
        Args:
            article (dict): Article with 'title' and 'content'
            
        Returns:
            dict: Quality analysis results
        """
        title = article.get('title', '').strip()
        content = article.get('content', '').strip()
        
        if not title or not content:
            return {'quality_score': 0, 'is_quality': False, 'reasons': ['Missing title or content']}
        
        analysis = {
            'length_analysis': self._analyze_length(title, content),
            'language_quality': self._analyze_language_quality(title, content),
            'content_structure': self._analyze_content_structure(content),
            'news_indicators': self._analyze_news_indicators(title, content),
            'junk_detection': self._detect_junk_content(title, content)
        }
        
        # Calculate overall quality score (0-100)
        quality_score = self._calculate_quality_score(analysis)
        
        # Determine if article meets quality threshold
        is_quality = quality_score >= 60  # Adjustable threshold
        
        # Generate reasons for decision
        reasons = self._generate_quality_reasons(analysis, is_quality)
        
        return {
            'quality_score': quality_score,
            'is_quality': is_quality,
            'reasons': reasons,
            'detailed_analysis': analysis
        }
    
    def classify_article(self, article):
        """
        Classify article into news categories using Enhanced Semantic Classification
        
        Args:
            article (dict): Article with 'title' and 'content'
            
        Returns:
            dict: Classification results
        """
        title = article.get('title', '').strip()
        content = article.get('content', '').strip()
        
        if not title or not content:
            return {'primary_category': 'general', 'confidence': 0, 'method': 'invalid_input'}
        
        # Try Zero-Shot Classification if available
        if self.use_zero_shot and self.zero_shot_classifier:
            try:
                result = self._classify_with_zero_shot(title, content)
                if result:
                    return result
            except Exception as e:
                print(f"Zero-Shot classification failed: {e}")
        
        # Use Enhanced Semantic Classification (primary method)
        return self._classify_with_enhanced_keywords(title, content)
    
    def _classify_with_enhanced_keywords(self, title, content):
        """
        Enhanced keyword-based classification with semantic understanding
        """
        title_lower = title.lower()
        content_lower = content.lower()
        combined_text = f"{title_lower} {content_lower}"
        
        # Calculate enhanced scores for each category
        category_scores = {}
        
        for category, data in self.enhanced_categories.items():
            score = 0
            
            # Primary keyword matches (higher weight)
            primary_matches = sum(1 for keyword in data['primary_keywords'] 
                                if keyword in combined_text)
            score += primary_matches * 3
            
            # Context keyword matches (lower weight)
            context_matches = sum(1 for keyword in data['context_keywords'] 
                                if keyword in combined_text)
            score += context_matches * 1.5
            
            # Title booster keywords (extra weight for title matches)
            title_boosts = sum(2 for keyword in data['title_boosters'] 
                             if keyword in title_lower)
            score += title_boosts * 2
            
            # Apply category weight
            score *= data['weight']
            
            # Semantic proximity bonus (keywords appearing near each other)
            proximity_bonus = self._calculate_proximity_bonus(
                combined_text, data['primary_keywords'] + data['context_keywords']
            )
            score += proximity_bonus
            
            category_scores[category] = score
        
        # Find primary category
        if not category_scores or max(category_scores.values()) == 0:
            return {
                'primary_category': 'general',
                'confidence': 0,
                'secondary_categories': [],
                'method': 'enhanced_semantic',
                'category_scores': category_scores
            }
        
        primary_category = max(category_scores, key=category_scores.get)
        primary_score = category_scores[primary_category]
        
        # Calculate confidence (0-100%)
        total_score = sum(category_scores.values())
        confidence = (primary_score / total_score * 100) if total_score > 0 else 0
        confidence = min(confidence, 95)  # Cap at 95% for keyword-based
        
        # Secondary categories
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        secondary_categories = [
            cat for cat, score in sorted_categories[1:3] 
            if score > primary_score * 0.3  # At least 30% of primary score
        ]
        
        return {
            'primary_category': primary_category,
            'confidence': round(confidence, 1),
            'secondary_categories': secondary_categories,
            'method': 'enhanced_semantic',
            'category_scores': {k: round(v, 2) for k, v in category_scores.items()}
        }
    
    def _calculate_proximity_bonus(self, text, keywords):
        """
        Calculate bonus points for keywords appearing close to each other
        """
        words = text.split()
        keyword_positions = []
        
        # Find positions of all keywords
        for i, word in enumerate(words):
            for keyword in keywords:
                if keyword in word:
                    keyword_positions.append(i)
        
        if len(keyword_positions) < 2:
            return 0
        
        # Calculate bonus based on keyword clustering
        keyword_positions.sort()
        proximity_bonus = 0
        
        for i in range(len(keyword_positions) - 1):
            distance = keyword_positions[i + 1] - keyword_positions[i]
            if distance <= 10:  # Keywords within 10 words of each other
                proximity_bonus += max(0, 2 - (distance / 5))
        
        return proximity_bonus
    
    def _classify_with_zero_shot(self, title, content):
        """
        Enhanced Zero-Shot Classification with better category descriptions
        """
        if not self.zero_shot_classifier:
            return None
            
        try:
            # Combine title and content, with title weighted more heavily
            text = f"{title} {title} {content}"  # Title appears twice for emphasis
            
            # Truncate if too long (BERT has token limits)
            words = text.split()
            if len(words) > 400:  # Conservative limit to stay under 512 tokens
                text = ' '.join(words[:400])
            
            # Enhanced category descriptions for better zero-shot performance
            categories = [
                "municipal government, city council, mayor, local politics, bylaw, city budget",
                "community festival, local events, cultural activities, neighborhood gathering", 
                "business, economics, employment, jobs, companies, labor strike, workers, union",
                "police, crime, emergency, accident, fire, arrest, intruder, break-in, safety",
                "weather, storm, climate, environment, pollution, conservation, temperature",
                "school, university, education, student, teacher, academic, learning",
                "healthcare, hospital, medical, health, doctor, patient, disease, treatment",
                "sports, hockey, team, player, game, tournament, athletics, coach"
            ]
            
            # Perform Zero-Shot classification
            result = self.zero_shot_classifier(text, categories)
            
            # Map results back to internal categories
            category_mapping = {
                "municipal government, city council, mayor, local politics, bylaw, city budget": "local_government",
                "community festival, local events, cultural activities, neighborhood gathering": "community_events",
                "business, economics, employment, jobs, companies, labor strike, workers, union": "business_economy",
                "police, crime, emergency, accident, fire, arrest, intruder, break-in, safety": "public_safety",
                "weather, storm, climate, environment, pollution, conservation, temperature": "environment_weather",
                "school, university, education, student, teacher, academic, learning": "education",
                "healthcare, hospital, medical, health, doctor, patient, disease, treatment": "health",
                "sports, hockey, team, player, game, tournament, athletics, coach": "sports"
            }
            
            # Get the top prediction
            top_category_desc = result['labels'][0]
            top_score = result['scores'][0]
            
            primary_category = category_mapping.get(top_category_desc, 'general')
            
            # Only use zero-shot if confidence is reasonable (>20%)
            if top_score < 0.20:
                print(f"Zero-shot confidence too low ({top_score*100:.1f}%), falling back to enhanced keywords")
                return None
            
            # Get secondary categories (other high-scoring ones)
            secondary_categories = []
            for i in range(1, min(3, len(result['labels']))):  # Top 2 secondary
                if result['scores'][i] > 0.15:  # Only if confidence > 15%
                    sec_cat = category_mapping.get(result['labels'][i])
                    if sec_cat:
                        secondary_categories.append(sec_cat)
            
            return {
                'primary_category': primary_category,
                'confidence': round(top_score * 100, 1),
                'secondary_categories': secondary_categories,
                'method': 'zero_shot',
                'all_scores': {
                    category_mapping.get(label, 'unknown'): round(score * 100, 1)
                    for label, score in zip(result['labels'], result['scores'])
                    if category_mapping.get(label)
                }
            }
        except Exception as e:
            print(f"Zero-Shot error: {e}")
            return None

    def extract_key_entities(self, article):
        """
        Extract key entities and information from article (basic NER)
        
        Args:
            article (dict): Article with 'title' and 'content'
            
        Returns:
            dict: Extracted entities and information
        """
        title = article.get('title', '')
        content = article.get('content', '')
        text = f"{title} {content}"
        
        entities = {
            'people': self._extract_people(text),
            'organizations': self._extract_organizations(text),
            'locations': self._extract_locations(text),
            'dates': self._extract_dates(text),
            'money_amounts': self._extract_money(text),
            'key_phrases': self._extract_key_phrases(title, content)
        }
        
        return entities
    
    def _analyze_length(self, title, content):
        """Analyze text length characteristics"""
        title_words = len(title.split())
        content_words = len(content.split())
        content_chars = len(content)
        
        return {
            'title_word_count': title_words,
            'content_word_count': content_words,
            'content_char_count': content_chars,
            'title_appropriate': 5 <= title_words <= 20,  # Good headline length
            'content_substantial': content_words >= 50,    # Minimum for news article
            'content_detailed': content_words >= 200       # Good detailed article
        }
    
    def _analyze_language_quality(self, title, content):
        """Analyze language quality and readability"""
        text = f"{title} {content}".lower()
        words = text.split()
        
        if not words:
            return {'score': 0, 'issues': ['No content']}
        
        # Calculate basic readability metrics
        sentences = len([s for s in re.split(r'[.!?]+', content) if s.strip()])
        avg_words_per_sentence = len(words) / max(sentences, 1)
        
        # Check for language quality issues
        issues = []
        
        # Too many repeated words
        word_counts = Counter(words)
        most_common = word_counts.most_common(5)
        if most_common and most_common[0][1] > len(words) * 0.1:  # Most common word > 10%
            issues.append('Highly repetitive content')
        
        # Sentences too long or too short on average
        if avg_words_per_sentence < 5:
            issues.append('Sentences too short (fragmented)')
        elif avg_words_per_sentence > 30:
            issues.append('Sentences too long (hard to read)')
        
        # Too many special characters (might be garbled)
        special_chars = sum(1 for c in text if not c.isalnum() and c not in ' \n\t.,!?;:-')
        if special_chars > len(text) * 0.1:
            issues.append('Too many special characters')
        
        # Calculate quality score
        base_score = 70
        base_score -= len(issues) * 15
        base_score = max(0, min(100, base_score))
        
        return {
            'score': base_score,
            'avg_words_per_sentence': avg_words_per_sentence,
            'issues': issues
        }
    
    def _analyze_content_structure(self, content):
        """Analyze content structure and organization"""
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        
        return {
            'paragraph_count': len(paragraphs),
            'sentence_count': len(sentences),
            'avg_sentences_per_paragraph': len(sentences) / max(len(paragraphs), 1),
            'well_structured': len(paragraphs) >= 2 and len(sentences) >= 3
        }
    
    def _analyze_news_indicators(self, title, content):
        """Look for indicators of legitimate news content"""
        text = f"{title} {content}".lower()
        
        scores = {}
        for category, indicators in self.quality_indicators.items():
            scores[category] = sum(1 for indicator in indicators if indicator in text)
        
        total_indicators = sum(scores.values())
        
        return {
            'indicator_scores': scores,
            'total_indicators': total_indicators,
            'has_journalistic_elements': scores.get('journalistic', 0) > 0,
            'has_temporal_elements': scores.get('temporal', 0) > 0,
            'has_factual_elements': scores.get('factual', 0) > 0
        }
    
    def _detect_junk_content(self, title, content):
        """Detect non-news junk content"""
        text = f"{title} {content}".lower()
        
        junk_found = [indicator for indicator in self.junk_indicators if indicator in text]
        junk_score = len(junk_found)
        
        return {
            'junk_indicators_found': junk_found,
            'junk_score': junk_score,
            'likely_junk': junk_score >= 2
        }
    
    def _calculate_quality_score(self, analysis):
        """Calculate overall quality score from analysis components"""
        score = 50  # Base score
        
        # Length analysis contribution
        length = analysis['length_analysis']
        if length['title_appropriate']:
            score += 10
        if length['content_substantial']:
            score += 15
        if length['content_detailed']:
            score += 10
        
        # Language quality contribution
        lang_quality = analysis['language_quality']
        score += (lang_quality['score'] - 50) * 0.3  # Scale language score contribution
        
        # Structure contribution
        structure = analysis['content_structure']
        if structure['well_structured']:
            score += 10
        
        # News indicators contribution
        news = analysis['news_indicators']
        score += min(news['total_indicators'] * 3, 20)  # Up to 20 points for news indicators
        
        # Junk detection penalty
        junk = analysis['junk_detection']
        if junk['likely_junk']:
            score -= 30
        else:
            score -= junk['junk_score'] * 5  # Penalty for each junk indicator
        
        return max(0, min(100, int(score)))
    
    def _generate_quality_reasons(self, analysis, is_quality):
        """Generate human-readable reasons for quality decision"""
        reasons = []
        
        if is_quality:
            if analysis['length_analysis']['content_detailed']:
                reasons.append('Substantial, detailed content')
            if analysis['news_indicators']['has_journalistic_elements']:
                reasons.append('Contains journalistic elements')
            if analysis['content_structure']['well_structured']:
                reasons.append('Well-structured article format')
            if analysis['language_quality']['score'] > 70:
                reasons.append('Good language quality')
        else:
            if not analysis['length_analysis']['content_substantial']:
                reasons.append('Content too short for news article')
            if analysis['junk_detection']['likely_junk']:
                reasons.append('Contains junk/navigation content')
            if analysis['language_quality']['score'] < 40:
                reasons.append('Poor language quality')
            if analysis['news_indicators']['total_indicators'] == 0:
                reasons.append('Lacks news-like characteristics')
        
        return reasons if reasons else ['General quality assessment']
    
    # Basic entity extraction methods (simple pattern-based approach)
    
    def _extract_people(self, text):
        """Extract potential person names (basic pattern matching)"""
        # Look for capitalized word patterns that might be names
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        potential_names = re.findall(name_pattern, text)
        
        # Filter out common false positives
        false_positives = {'New York', 'North America', 'United States', 'Great Lakes', 'City Council'}
        names = [name for name in potential_names if name not in false_positives]
        
        return list(set(names))[:10]  # Limit to top 10 unique names
    
    def _extract_organizations(self, text):
        """Extract potential organization names"""
        org_patterns = [
            r'\b[A-Z][a-z]+ (?:Inc|Corp|Corporation|Company|Ltd|Limited|LLC)\b',
            r'\b[A-Z][a-z]+ (?:University|College|School|Hospital|Department)\b',
            r'\b(?:City of|Town of) [A-Z][a-z]+\b'
        ]
        
        organizations = []
        for pattern in org_patterns:
            organizations.extend(re.findall(pattern, text))
        
        return list(set(organizations))[:10]
    
    def _extract_locations(self, text):
        """Extract potential location names"""
        # Common Canadian locations and patterns
        canadian_locations = [
            'Sudbury', 'Toronto', 'Ottawa', 'Montreal', 'Vancouver', 'Calgary',
            'Edmonton', 'Winnipeg', 'Halifax', 'Ontario', 'Quebec', 'Alberta',
            'British Columbia', 'Manitoba', 'Saskatchewan', 'Nova Scotia',
            'New Brunswick', 'Newfoundland', 'Canada'
        ]
        
        found_locations = [loc for loc in canadian_locations if loc.lower() in text.lower()]
        
        # Also look for "City of X" or "Town of X" patterns
        city_pattern = r'(?:City of|Town of) ([A-Z][a-z]+)'
        cities = re.findall(city_pattern, text)
        found_locations.extend(cities)
        
        return list(set(found_locations))[:10]
    
    def _extract_dates(self, text):
        """Extract dates and time references"""
        date_patterns = [
            r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? \d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b(?:today|yesterday|tomorrow|this week|last week|next week)\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(dates))[:5]
    
    def _extract_money(self, text):
        """Extract monetary amounts"""
        money_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'\b\d+(?:,\d{3})*(?:\.\d{2})? dollars?\b',
            r'\b\d+(?:,\d{3})*(?:\.\d{2})? million\b',
            r'\b\d+(?:,\d{3})*(?:\.\d{2})? billion\b'
        ]
        
        amounts = []
        for pattern in money_patterns:
            amounts.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(amounts))[:5]
    
    def _extract_key_phrases(self, title, content):
        """Extract key phrases and important terms"""
        # Combine title (weighted higher) with content
        title_words = title.lower().split()
        content_words = content.lower().split()
        
        # Count word frequency, giving title words more weight
        word_freq = Counter()
        for word in title_words:
            if len(word) > 3 and word.isalpha():  # Skip short words and numbers
                word_freq[word] += 3  # Title words get 3x weight
        
        for word in content_words:
            if len(word) > 3 and word.isalpha():
                word_freq[word] += 1
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'this', 'that', 'these', 'those', 'they', 'them', 'their', 'there', 'where',
            'when', 'what', 'who', 'how', 'why', 'which', 'while', 'during', 'after',
            'before', 'above', 'below', 'over', 'under', 'between', 'through', 'into'
        }
        
        filtered_words = {word: freq for word, freq in word_freq.items() if word not in stop_words}
        
        # Return top key phrases
        return [word for word, freq in Counter(filtered_words).most_common(10)]
