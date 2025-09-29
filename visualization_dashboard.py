#!/usr/bin/env python3
"""
Visualization Dashboard for Multimodal Analysis Results
Creates interactive visualizations for sentiment, truth, acoustic analysis, and correlations
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class MultimodalVisualizationDashboard:
    """Comprehensive visualization dashboard for multimodal analysis results"""
    
    def __init__(self, results_file: str = None):
        self.results_file = results_file
        self.results_data = None
        self.fig_size = (15, 10)
        
        # Load results if file provided
        if results_file and os.path.exists(results_file):
            self.load_results(results_file)
    
    def load_results(self, results_file: str):
        """Load multimodal analysis results from JSON file"""
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                self.results_data = json.load(f)
            print(f"✅ Loaded results from: {results_file}")
        except Exception as e:
            print(f"❌ Error loading results: {e}")
            self.results_data = None
    
    def create_assessment_radar_chart(self, save_path: str = None):
        """Create radar chart for final assessment scores"""
        if not self.results_data:
            print("❌ No results data available")
            return
        
        assessment = self.results_data.get('final_assessment', {})
        
        # Prepare data for radar chart
        categories = []
        values = []
        
        for key, value in assessment.items():
            categories.append(key.replace('_', ' ').title())
            values.append(value)
        
        # Number of variables
        N = len(categories)
        
        # Compute angle for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the circle
        
        # Add first value to end to close the radar chart
        values += values[:1]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
        
        # Plot the radar chart
        ax.plot(angles, values, 'o-', linewidth=2, label='Assessment Scores', color='#FF6B6B')
        ax.fill(angles, values, alpha=0.25, color='#FF6B6B')
        
        # Add category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        
        # Set y-axis limits
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8)
        ax.grid(True)
        
        # Add title
        plt.title('Multimodal Analysis - Final Assessment Radar Chart', 
                 size=16, fontweight='bold', pad=20)
        
        # Add legend
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Radar chart saved to: {save_path}")
        
        plt.show()
    
    def create_correlation_heatmap(self, save_path: str = None):
        """Create heatmap showing correlations between different modalities"""
        if not self.results_data:
            print("❌ No results data available")
            return
        
        # Extract correlation data
        summary = self.results_data.get('summary', {})
        assessment = self.results_data.get('final_assessment', {})
        
        # Create correlation matrix data
        correlation_data = {
            'Sentiment Confidence': summary.get('sentiment_confidence', 0),
            'Truth Likelihood': summary.get('truth_likelihood', 0),
            'Voice Quality': summary.get('voice_quality', 0),
            'Emotional Authenticity': summary.get('emotional_authenticity', 0),
            'Multimodal Consistency': summary.get('multimodal_consistency', 0),
            'Overall Credibility': assessment.get('overall_credibility', 0),
            'Stress Level': 1.0 - summary.get('stress_level', 0),  # Invert for positive correlation
            'Deception Risk': 1.0 - summary.get('deception_likelihood', 0)  # Invert for positive correlation
        }
        
        # Create synthetic correlation matrix (in real implementation, use actual correlations)
        metrics = list(correlation_data.keys())
        values = list(correlation_data.values())
        
        # Create correlation matrix
        correlation_matrix = np.zeros((len(metrics), len(metrics)))
        for i in range(len(metrics)):
            for j in range(len(metrics)):
                if i == j:
                    correlation_matrix[i][j] = 1.0
                else:
                    # Simple correlation based on value similarity
                    correlation_matrix[i][j] = 1.0 - abs(values[i] - values[j])
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        sns.heatmap(correlation_matrix, 
                   mask=mask,
                   annot=True, 
                   cmap='RdYlBu_r', 
                   center=0,
                   square=True,
                   xticklabels=metrics,
                   yticklabels=metrics,
                   cbar_kws={"shrink": .8},
                   fmt='.2f')
        
        plt.title('Multimodal Analysis - Cross-Modal Correlations', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"🔥 Correlation heatmap saved to: {save_path}")
        
        plt.show()
    
    def create_psychological_state_chart(self, save_path: str = None):
        """Create bar chart for speaker psychological state"""
        if not self.results_data:
            print("❌ No results data available")
            return
        
        assessment = self.results_data.get('final_assessment', {})
        
        # Extract psychological indicators
        psychological_metrics = {
            'Emotional Stability': 1.0 - assessment.get('stress_level', 0),
            'Confidence Level': assessment.get('confidence_score', 0),
            'Cognitive Clarity': assessment.get('cognitive_clarity', 0),
            'Authenticity': assessment.get('emotional_authenticity', 0),
            'Voice Control': assessment.get('voice_quality', 0),
            'Psychological Wellness': assessment.get('psychological_wellness', 0)
        }
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(14, 8))
        
        metrics = list(psychological_metrics.keys())
        values = list(psychological_metrics.values())
        
        # Color code based on values
        colors = []
        for value in values:
            if value >= 0.7:
                colors.append('#4CAF50')  # Green for good
            elif value >= 0.4:
                colors.append('#FF9800')  # Orange for moderate
            else:
                colors.append('#F44336')  # Red for poor
        
        bars = ax.bar(metrics, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Customize chart
        ax.set_ylabel('Score (0-1)', fontsize=12, fontweight='bold')
        ax.set_title('Speaker Psychological State Analysis', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylim(0, 1.1)
        ax.grid(axis='y', alpha=0.3)
        
        # Add horizontal reference lines
        ax.axhline(y=0.7, color='green', linestyle='--', alpha=0.5, label='Good (≥0.7)')
        ax.axhline(y=0.4, color='orange', linestyle='--', alpha=0.5, label='Moderate (≥0.4)')
        
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"🧠 Psychological state chart saved to: {save_path}")
        
        plt.show()
    
    def create_timeline_analysis(self, save_path: str = None):
        """Create timeline showing analysis progression and key metrics"""
        if not self.results_data:
            print("❌ No results data available")
            return
        
        # Simulate processing timeline (in real implementation, use actual timestamps)
        processing_stages = [
            'Text Input',
            'Sentiment Analysis',
            'Truth Analysis', 
            'Acoustic Analysis',
            'Multimodal Correlation',
            'Final Assessment'
        ]
        
        # Get processing times (simulated progression)
        total_time = self.results_data.get('processing_time', 600)
        stage_times = [0, total_time * 0.4, total_time * 0.8, total_time * 0.9, total_time * 0.95, total_time]
        
        # Key metrics at each stage
        sentiment_score = self.results_data.get('summary', {}).get('sentiment_confidence', 0)
        truth_score = self.results_data.get('summary', {}).get('truth_likelihood', 0)
        voice_score = self.results_data.get('summary', {}).get('voice_quality', 0)
        consistency_score = self.results_data.get('summary', {}).get('multimodal_consistency', 0)
        credibility_score = self.results_data.get('final_assessment', {}).get('overall_credibility', 0)
        
        metric_progression = [0, sentiment_score, truth_score, voice_score, consistency_score, credibility_score]
        
        # Create timeline plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        # Processing timeline
        ax1.plot(stage_times, range(len(processing_stages)), 'o-', linewidth=3, markersize=8, color='#2196F3')
        ax1.set_yticks(range(len(processing_stages)))
        ax1.set_yticklabels(processing_stages)
        ax1.set_ylabel('Processing Stages', fontweight='bold')
        ax1.set_title('Multimodal Analysis Processing Timeline', fontsize=16, fontweight='bold', pad=20)
        ax1.grid(True, alpha=0.3)
        
        # Add processing time annotations
        for i, (time, stage) in enumerate(zip(stage_times, processing_stages)):
            if i > 0:
                duration = stage_times[i] - stage_times[i-1]
                ax1.annotate(f'{duration:.1f}s', 
                           xy=(time, i), xytext=(10, 10), 
                           textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                           fontsize=8)
        
        # Metric progression
        ax2.plot(stage_times, metric_progression, 's-', linewidth=3, markersize=8, color='#FF5722')
        ax2.fill_between(stage_times, metric_progression, alpha=0.3, color='#FF5722')
        ax2.set_xlabel('Time (seconds)', fontweight='bold')
        ax2.set_ylabel('Analysis Score', fontweight='bold')
        ax2.set_title('Analysis Score Progression', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 1)
        ax2.grid(True, alpha=0.3)
        
        # Add final score annotation
        final_score = metric_progression[-1]
        ax2.annotate(f'Final Score: {final_score:.3f}', 
                    xy=(stage_times[-1], final_score), 
                    xytext=(-50, 20), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                    fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"⏱️ Timeline analysis saved to: {save_path}")
        
        plt.show()
    
    def create_comprehensive_dashboard(self, output_dir: str = "visualizations"):
        """Create comprehensive dashboard with all visualizations"""
        if not self.results_data:
            print("❌ No results data available")
            return
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print("🎨 Creating Comprehensive Multimodal Analysis Dashboard")
        print("=" * 60)
        
        # Generate timestamp for file naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create all visualizations
        print("📊 1. Creating Assessment Radar Chart...")
        self.create_assessment_radar_chart(
            save_path=os.path.join(output_dir, f"assessment_radar_{timestamp}.png")
        )
        
        print("🔥 2. Creating Correlation Heatmap...")
        self.create_correlation_heatmap(
            save_path=os.path.join(output_dir, f"correlation_heatmap_{timestamp}.png")
        )
        
        print("🧠 3. Creating Psychological State Chart...")
        self.create_psychological_state_chart(
            save_path=os.path.join(output_dir, f"psychological_state_{timestamp}.png")
        )
        
        print("⏱️ 4. Creating Timeline Analysis...")
        self.create_timeline_analysis(
            save_path=os.path.join(output_dir, f"timeline_analysis_{timestamp}.png")
        )
        
        # Create summary report
        self.create_summary_report(
            save_path=os.path.join(output_dir, f"analysis_summary_{timestamp}.txt")
        )
        
        print(f"\n✅ Dashboard created successfully!")
        print(f"📁 All visualizations saved to: {output_dir}")
        
        return output_dir
    
    def create_summary_report(self, save_path: str = None):
        """Create text summary report of the analysis"""
        if not self.results_data:
            print("❌ No results data available")
            return
        
        summary = self.results_data.get('summary', {})
        assessment = self.results_data.get('final_assessment', {})
        recommendations = self.results_data.get('recommendations', [])
        
        report = f"""
MULTIMODAL ANALYSIS SUMMARY REPORT
{'='*50}

Analysis Timestamp: {self.results_data.get('analysis_timestamp', 'Unknown')}
Audio File: {self.results_data.get('audio_file', 'Unknown')}
Processing Time: {self.results_data.get('processing_time', 0):.2f} seconds

TEXT ANALYSIS SUMMARY:
- Overall Sentiment: {summary.get('overall_sentiment', 'Unknown')}
- Sentiment Confidence: {summary.get('sentiment_confidence', 0):.3f}
- Truth Likelihood: {summary.get('truth_likelihood', 0):.3f}
- Truth Confidence: {summary.get('truth_confidence', 0):.3f}

ACOUSTIC ANALYSIS SUMMARY:
- Voice Quality: {summary.get('voice_quality', 0):.3f}
- Stress Level: {summary.get('stress_level', 0):.3f}
- Deception Likelihood: {summary.get('deception_likelihood', 0):.3f}

MULTIMODAL INTEGRATION:
- Emotional Authenticity: {summary.get('emotional_authenticity', 0):.3f}
- Multimodal Consistency: {summary.get('multimodal_consistency', 0):.3f}

FINAL ASSESSMENT:
- Overall Credibility: {assessment.get('overall_credibility', 0):.3f}
- Psychological Wellness: {assessment.get('psychological_wellness', 0):.3f}
- Cognitive Clarity: {assessment.get('cognitive_clarity', 0):.3f}

RECOMMENDATIONS:
"""
        
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"\n{'='*50}\nReport generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Summary report saved to: {save_path}")
        else:
            print(report)
        
        return report

def main():
    """Test the visualization dashboard"""
    # Find the most recent multimodal analysis results file
    results_files = [f for f in os.listdir('.') if f.startswith('multimodal_analysis_results_') and f.endswith('.json')]
    
    if not results_files:
        print("❌ No multimodal analysis results files found")
        print("💡 Please run multimodal_analysis_system.py first to generate results")
        return
    
    # Use the most recent file
    latest_file = sorted(results_files)[-1]
    print(f"📊 Using results file: {latest_file}")
    
    # Create dashboard
    dashboard = MultimodalVisualizationDashboard(latest_file)
    
    # Create comprehensive dashboard
    output_dir = dashboard.create_comprehensive_dashboard()
    
    print(f"\n🎯 Visualization Dashboard Complete!")
    print(f"📁 Check the '{output_dir}' folder for all generated visualizations")

if __name__ == "__main__":
    main()