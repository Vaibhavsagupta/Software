from database import SessionLocal
import models

def seed_price_list():
    db = SessionLocal()
    
    categories = [
        "ACRYLIC", "ACRYLIC COMPLETE DENTURE", "ACRYLIC FACING", "BILATERAL DENTURE FRAME", 
        "BITE RIMS", "BITE SPLINT", "BLEACHING TRAY", "CEMENT RETAIN PFM", "CERAMIC", 
        "COLD CURE REPAIR", "DUPLICATION OF CASTS", "DURACETAL PARTIAL DENTURE", 
        "DURAFLEX PARTIAL DENTURE", "EMAX VENEER", "FLEXIBLE", "FLEXIBLE RPD BITE RIM U/L", 
        "FLEXIBLE RPD REPAIR", "FULL METAL", "FULL PALATAL COVERAGE FRAME", "HABIT BREAKER", 
        "HAWLEY'S APPLIANCE", "HAWLY\"S APPLIANCE WITH EXPANSION SCREW", "HYBRID DENTURE", 
        "IN LAY", "MATERIALS", "METAL", "METAL TRAIL", "MONILITHIUM", "ORTHO", 
        "ORTHO RETRACTER", "PFM", "PFM FACING", "SCAN", "SOLDERED TPA MOLAR TUBE", 
        "SPACE MAINTAINER REPAIR", "SPACE MAINTAINER WITH RPD", "STUDY MODEL", 
        "ZIRCON CORE CUTBACK", "ZIRCON REPAIR", "ZIRCONIUM"
    ]
    
    # Add Categories
    cat_map = {}
    for cat_name in categories:
        cat = db.query(models.ProductCategory).filter(models.ProductCategory.name == cat_name).first()
        if not cat:
            cat = models.ProductCategory(name=cat_name)
            db.add(cat)
            db.commit()
            db.refresh(cat)
        cat_map[cat_name] = cat.id
        
    # Sample Products from the list
    products = [
        ("CERAMIC", "CERAMIC", "0"),
        ("CERAMIC", "CERAMIC REPAIR", "5"),
        ("CERAMIC", "MARYLAND", "15"),
        ("PFM", "PFM", "7"),
        ("PFM", "PFM (PRECIOUS)", "10"),
        ("PFM", "IMPLANT PFM", "12"),
        ("PFM", "PFM BISQUE TRIAL", "0"),
        ("ORTHO", "HAWLEY'S APPLIANCE", "8"),
        ("ORTHO", "CLEAR RETAINER U/L", "25"),
        ("ZIRCONIUM", "ZIRCON", "30"),
        ("ZIRCONIUM", "ZIRCON CORE", "0"),
        ("ACRYLIC", "ACRYLIC CROWN", "5"),
        ("FLEXIBLE", "FLEXIBLE RPD", "20"),
    ]
    
    for cat_name, prod_name, default_charge in products:
        if cat_name in cat_map:
            exists = db.query(models.ProductPrice).filter(
                models.ProductPrice.name == prod_name, 
                models.ProductPrice.category_id == cat_map[cat_name]
            ).first()
            if not exists:
                db.add(models.ProductPrice(
                    category_id=cat_map[cat_name],
                    name=prod_name,
                    charge=float(default_charge)
                ))
                
    db.commit()
    print("Price list seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_price_list()
