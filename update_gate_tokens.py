from app import app, db
from models import SubRegion

with app.app_context():
    # Add the gate_device_token column to the subregions table
    print("Adding gate_device_token column to subregions table...")
    
    try:
        # Execute raw SQL to add the column
        with db.engine.connect() as conn:
            # Check if column exists
            result = conn.execute(db.text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'subregions'
                AND COLUMN_NAME = 'gate_device_token'
            """))
            
            column_exists = result.fetchone()[0] > 0
            
            if not column_exists:
                # Add the column
                conn.execute(db.text("""
                    ALTER TABLE subregions
                    ADD COLUMN gate_device_token VARCHAR(8) UNIQUE
                """))
                conn.commit()
                print("✓ Column added successfully!")
            else:
                print("✓ Column already exists!")
        
        # Now generate tokens for subregions that don't have them
        print("\nGenerating gate tokens for subregions...")
        subregions = SubRegion.query.all()
        
        updated_count = 0
        for subregion in subregions:
            if not subregion.gate_device_token:
                subregion.generate_gate_token()
                updated_count += 1
                print(f"  ✓ {subregion.name}: {subregion.gate_device_token}")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✓ Added gate tokens to {updated_count} subregions!")
        else:
            print("\n✓ All subregions already have gate tokens!")
        
        # Display all gate tokens
        print("\n" + "="*60)
        print("GATE TOKENS FOR ESP32-CAM DEVICES")
        print("="*60)
        
        all_subregions = SubRegion.query.all()
        for sr in all_subregions:
            print(f"\n📍 {sr.region.city.name} → {sr.region.name} → {sr.name}")
            print(f"   Gate Token: {sr.gate_device_token}")
        
        print("\n" + "="*60)
        print("Copy these tokens to your ESP32-CAM devices!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.session.rollback()